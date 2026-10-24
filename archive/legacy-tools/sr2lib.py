"""SR2 Simplified-Chinese patcher - core library.

Verified facts this relies on
------------------------------
charlist_CH.txt   : inside patch.vpp_pc @0x64D310, 19727 bytes
                    header comment, "count=N", then N decimal codepoints
fnt_chinese.vf3_pc: @0xFD19B0, 68300 bytes
                    'VFNT' + 0xD0 header, then N*16-byte character records
fnt_chinese.g_peg_pc: @0xBD19B0, 4194304 bytes = 2048x2048 DXT3 (BC2)
glyph atlas layout:
    row 0     : 94 ASCII glyphs (own variable pitch)
    rows 1..  : 66 glyphs per row, pitch 31
    position  : x = 2 + 31*col, y = 34 + 31*row   (for index >= 94)
    index     : charvalue == glyph index == charlist index
font descriptor (pegs.vpp_pc @0x7D0A0, 94 bytes):
    'GEKV', size=94, dataSize, 1, 1, 16, 0, w=2048, h=2048, fmt=401(dxt3), name
VPP container: Kaitai saints_row_2_vpp_pc; append-and-repoint is safe.
"""
import struct, os, re
import numpy as np

# ---------------------------------------------------------------- constants
MAGIC_VPP = bytes([0xCE, 0x0A, 0x89, 0x51, 0x04])

CL_OFF, CL_LEN = 0x64D310, 19727
VF_OFF, VF_LEN = 0xFD19B0, 68300
AT_OFF, AT_LEN = 0xBD19B0, 4194304

ATLAS_W = ATLAS_H = 2048
PITCH = 31
ASCII_COUNT = 94
CJK_COLS = 66
CJK_X0, CJK_Y0 = 2, 34
DXT3_BLOCK = 16


# ---------------------------------------------------------------- charlist
def parse_charlist(buf):
    """Return list of codepoints from a charlist_CH.txt blob."""
    m = re.search(rb'count=(\d+)\r\n', buf)
    start = m.end()
    body = buf[start:]
    end = body.find(b'//ENDOFFILE')
    if end < 0:
        end = len(body)
    return [int(x) for x in re.findall(rb'\d+', body[:end])]


def build_charlist(codepoints, comment=None):
    """Serialise a charlist_CH.txt."""
    if comment is None:
        comment = (b"//Used character list based on file "
                   b"'d:\\projects\\sr2\\main\\data\\tables\\localized_exports\\platform_pc_CH.txt'\r\n"
                   b"// a list of all characters known to be used in Saint's Row.\r\n"
                   b"// used to compress from 65536 Unicode\r\n")
    out = bytearray(comment)
    out += b'count=%d\r\n' % len(codepoints)
    out += b'\r\n'.join(str(c).encode() for c in codepoints)
    out += b'\r\n//ENDOFFILE\r\n'
    return bytes(out)


# ---------------------------------------------------------------- font def
def parse_vfnt(buf):
    """Return (header_bytes, [ (spacing, byteWidth, offset, kerning), ... ])."""
    assert buf[:4] == b'VFNT', buf[:4]
    count = struct.unpack_from('<I', buf, 8)[0]
    header = buf[:0xD0]
    recs = []
    for k in range(count):
        o = 0xD0 + k * 16
        recs.append(struct.unpack_from('<IIII', buf, o))
    tail = buf[0xD0 + count * 16:]
    return header, recs, tail


def build_vfnt(header, recs, tail=None):
    out = bytearray(header)
    out[8:12] = struct.pack('<I', len(recs))
    for r in recs:
        out += struct.pack('<IIII', *r)
    if tail:
        out += tail
    return bytes(out)


# ---------------------------------------------------------------- DXT3
def _rgb565(v):
    r = ((v >> 11) & 0x1F) * 255 // 31
    g = ((v >> 5) & 0x3F) * 255 // 63
    b = (v & 0x1F) * 255 // 31
    return int(r), int(g), int(b)


def dxt3_decode(data, w, h):
    """Return (rgb uint8 h,w,3, alpha uint8 h,w)."""
    bw, bh = w // 4, h // 4
    blk = np.frombuffer(data, np.uint8)[:bw * bh * 16].reshape(bh, bw, 16)
    rgb = np.zeros((h, w, 3), np.uint8)
    alpha = np.zeros((h, w), np.uint8)
    for by in range(bh):
        for bx in range(bw):
            b = blk[by, bx]
            c0 = int(b[8]) | (int(b[9]) << 8)
            c1 = int(b[10]) | (int(b[11]) << 8)
            idx = int.from_bytes(b[12:16].tobytes(), 'little')
            r0, g0, b0 = _rgb565(c0)
            r1, g1, b1 = _rgb565(c1)
            if c0 > c1:
                pal = [(r0, g0, b0), (r1, g1, b1),
                       ((2*r0+r1)//3, (2*g0+g1)//3, (2*b0+b1)//3),
                       ((r0+2*r1)//3, (g0+2*g1)//3, (b0+2*b1)//3)]
            else:
                pal = [(r0, g0, b0), (r1, g1, b1),
                       ((r0+r1)//2, (g0+g1)//2, (b0+b1)//2), (0, 0, 0)]
            for py in range(4):
                for px in range(4):
                    k = py * 4 + px
                    r, g, bb = pal[(idx >> (2*k)) & 3]
                    Y, X = by*4+py, bx*4+px
                    rgb[Y, X] = (r, g, bb)
                    a4 = (int(b[k // 2]) >> (4 * (k % 2))) & 0xF
                    alpha[Y, X] = a4 * 17
    return rgb, alpha


def dxt3_encode(rgb, alpha):
    """Encode rgb(h,w,3) + alpha(h,w) to DXT3 bytes (BC2).

    DXT3 = 8 bytes explicit 4-bit alpha + 8 bytes DXT1 colour.

    This atlas uses PREMULTIPLIED alpha: the colour channel mirrors the coverage,
    i.e. RGB == (a,a,a) for every pixel.  Verified directly, e.g. a=102 -> rgb
    (35,35,35) and a=170 -> rgb (106,105,106) on a real glyph.

    Consequences:
      * the coverage really is the explicit alpha (8 bytes, 4 bits/pixel);
      * the colour must stay greyscale and follow the alpha, otherwise the glyph
        renders fully transparent - which is what made the whole UI lose its text.

    The colour block is therefore built in DXT1's *3-colour* mode:
        c0 = max alpha in the block   (the ink grey)
        c1 = 0
        1/3 point = c0/3,  2/3 point = 2*c0/3
    so index 0 / 2 / 3 give c0, 2c0/3, c0/3 - a cheap 2-bit greyscale ramp that
    the 4-bit explicit alpha refines.  Index 1 is unused.
    """
    h, w = alpha.shape
    bw, bh = w // 4, h // 4

    a16 = np.asarray(alpha, dtype=np.uint16)
    # per-block max alpha -> the ink grey for that block (RGB565, greyscale)
    mx = a16.reshape(bh, 4, bw, 4).max(axis=(1, 3)).astype(np.uint16)   # (bh,bw)
    lum = np.minimum(mx, 248)                                            # keep c0>c1
    # greyscale RGB565 with r5 == g6 == b5 == v
    v5 = np.clip(lum >> 3, 0, 31)
    v6 = np.clip(lum >> 2, 0, 63)
    grey = ((v5 << 11) | (v6 << 5) | v5).astype(np.uint16)

    # ---- explicit 4-bit alpha ----
    a4 = (a16 >> 4).astype(np.uint8)
    a4 = a4.reshape(bh, 4, bw, 4).transpose(0, 2, 1, 3).reshape(bh, bw, 16)
    a_bytes = (a4[:, :, 0::2] | (a4[:, :, 1::2] << 4)).astype(np.uint8)

    # ---- DXT1 colour indices ----
    L = np.clip(lum, 1, 255).astype(np.float32)
    t1 = 2.0 * L / 3.0            # palette index 2
    t2 = L / 3.0                  # palette index 3
    q = a16.reshape(bh, 4, bw, 4).transpose(0, 2, 1, 3).reshape(bh, bw, 16).astype(np.float32)
    d0 = np.abs(q - L[:, :, None])
    d2 = np.abs(q - t1[:, :, None])
    d3 = np.abs(q - t2[:, :, None])
    pick = np.argmin(np.stack([d0, d2, d3], axis=-1), axis=-1)   # 0,1,2
    idx = np.where(pick == 0, 0, np.where(pick == 1, 2, 3)).astype(np.uint32)

    words = np.zeros((bh, bw), np.uint32)
    for k in range(16):
        words |= (idx[:, :, k] & 3) << (2 * k)

    blocks = np.zeros((bh, bw, 16), np.uint8)
    blocks[:, :, 0:8] = a_bytes
    blocks[:, :, 8] = (grey & 0xFF).astype(np.uint8)
    blocks[:, :, 9] = (grey >> 8).astype(np.uint8)
    blocks[:, :, 10] = 0
    blocks[:, :, 11] = 0
    blocks[:, :, 12] = (words & 0xFF).astype(np.uint8)
    blocks[:, :, 13] = ((words >> 8) & 0xFF).astype(np.uint8)
    blocks[:, :, 14] = ((words >> 16) & 0xFF).astype(np.uint8)
    blocks[:, :, 15] = ((words >> 24) & 0xFF).astype(np.uint8)
    return blocks.tobytes()


# ---------------------------------------------------------------- VPP
class Vpp:
    def __init__(self, path):
        self.path = path
        self.data = bytearray(open(path, 'rb').read())
        d = self.data
        assert d[:5] == MAGIC_VPP, 'not an SR2 VPP'
        o = 5 + 0x14F
        (self.num, self.container_size, self.len_offsets,
         self.len_filenames, self.len_extensions) = struct.unpack_from('<iiiii', d, o)
        self.names_at = ((0x800 + self.len_offsets) & 0xFFFFF800) + 0x800
        self.ext_at = ((self.names_at + self.len_filenames) & 0xFFFFF800) + 0x800
        self.data_start = ((self.ext_at + self.len_extensions) & 0xFFFFF800) + 0x800

    def _strz(self, base, pos):
        e = self.data.find(b'\x00', base + pos)
        return self.data[base + pos:e].decode('ascii', 'replace')

    def entries(self):
        out = []
        for i in range(self.num):
            e = 0x800 + i * 28
            a, b, c, d, ln, m1, z = struct.unpack_from('<IIiiiii', self.data, e)
            out.append(dict(idx=i, name=self._strz(self.names_at, a),
                            ext=self._strz(self.ext_at, b) if b else '',
                            body=d, size=ln, entry_off=e))
        return out

    def read(self, ent):
        p = self.data_start + ent['body']
        return bytes(self.data[p:p + ent['size']])

    def find(self, name, ext=None):
        for e in self.entries():
            if e['name'].lower() == name.lower() and (ext is None or e['ext'].lower() == ext.lower()):
                return e
        return None

    def replace_body_appended(self, ent, payload, align=0x800):
        """Write payload at the end of the file and repoint the entry."""
        d = self.data
        pad = (-len(d)) % align
        d += b'\x00' * pad
        new_body = len(d) - self.data_start
        d += payload
        struct.pack_into('<i', d, ent['entry_off'] + 12, new_body)
        struct.pack_into('<i', d, ent['entry_off'] + 16, len(payload))
        struct.pack_into('<i', d, 5 + 0x14F + 4, len(d))     # container_size
        return ent

    def save(self, path):
        open(path, 'wb').write(bytes(self.data))
