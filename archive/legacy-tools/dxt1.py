"""DXT1 (BC1) encoder for a 1-bit-alpha glyph atlas.

WHY DXT1
    Juiced caps the font GPU pool at 9 MB, so a 2048x2048 DXT3 atlas (4 MiB) cannot
    grow to 4096x4096 DXT3 (16 MiB).  DXT1 is 8:1 instead of 4:1, so
    2048x4096 DXT1 is only 4 MiB - exactly what the shipped atlas already costs.

FORMAT
    DXT1 block = 8 bytes: u16 c0, u16 c1, u32 2-bit indices.
    We use the 4-COLOUR mode (c0 > c1) so index 3 means transparent black:
        c0 = ink colour (RGB565)
        c1 = 0 (black)
        index 0 -> c0            (opaque glyph)
        index 1 -> c1            (unused)
        index 2 -> 2/3 c0        (unused)
        index 3 -> transparent   (background)
    That gives hard-edged glyphs, which is the trade-off for halving the memory.
"""
import numpy as np


def _to565(r, g, b):
    return ((int(r) >> 3) << 11) | ((int(g) >> 2) << 5) | (int(b) >> 3)


def dxt1_encode(rgb, alpha, thresh=128, ink=None):
    """Encode rgb(h,w,3) + alpha(h,w) into DXT1 (BC1) bytes with 1-bit alpha.

    Pixels with alpha >= thresh become the ink colour, the rest transparent.
    `ink` overrides the ink colour; by default it is derived from the opaque
    pixels of the source so the result matches the shipped atlas.
    """
    h, w = alpha.shape
    assert h % 4 == 0 and w % 4 == 0, (h, w)
    bw, bh = w // 4, h // 4

    if ink is None:
        m = alpha > thresh
        if m.sum() == 0:
            ink = (255, 255, 255)
        else:
            ink = tuple(int(round(v)) for v in np.rint(rgb[m].mean(axis=0)))
    c0 = _to565(*ink)
    c1 = 0
    if c0 <= c1:                 # c0 must be greater for 4-colour mode
        c0 = 1

    opaque = (alpha >= thresh)                                   # (h,w) bool
    # per-block 16-bit index mask: bit 2k set -> pixel k is transparent (index 3)
    ok = opaque.reshape(bh, 4, bw, 4).transpose(0, 2, 1, 3).reshape(bh, bw, 16)
    words = np.zeros((bh, bw), np.uint32)
    for k in range(16):
        # index 3 for transparent, 0 for opaque
        words |= (np.where(ok[:, :, k], 0, 3).astype(np.uint32) << (2 * k))

    blocks = np.zeros((bh, bw, 8), np.uint8)
    blocks[:, :, 0] = c0 & 0xFF
    blocks[:, :, 1] = (c0 >> 8) & 0xFF
    blocks[:, :, 2] = c1 & 0xFF
    blocks[:, :, 3] = (c1 >> 8) & 0xFF
    blocks[:, :, 4] = (words & 0xFF).astype(np.uint8)
    blocks[:, :, 5] = ((words >> 8) & 0xFF).astype(np.uint8)
    blocks[:, :, 6] = ((words >> 16) & 0xFF).astype(np.uint8)
    blocks[:, :, 7] = ((words >> 24) & 0xFF).astype(np.uint8)
    return blocks.tobytes()


def dxt1_decode(data, w, h):
    """Reference decoder, for self-checking only."""
    bw, bh = w // 4, h // 4
    blk = np.frombuffer(data, np.uint8)[:bw * bh * 8].reshape(bh, bw, 8)
    rgb = np.zeros((h, w, 3), np.uint8)
    alpha = np.zeros((h, w), np.uint8)
    for by in range(bh):
        for bx in range(bw):
            b = blk[by, bx]
            c0 = int(b[0]) | (int(b[1]) << 8)
            c1 = int(b[2]) | (int(b[3]) << 8)
            idx = int.from_bytes(b[4:8].tobytes(), 'little')
            def dec(v):
                return (((v >> 11) & 31) * 255 // 31,
                        ((v >> 5) & 63) * 255 // 63,
                        (v & 31) * 255 // 31)
            r0, g0, b0 = dec(c0)
            r1, g1, b1 = dec(c1)
            if c0 > c1:
                pal = [(r0, g0, b0), (r1, g1, b1),
                       ((2*r0+r1)//3, (2*g0+g1)//3, (2*b0+b1)//3),
                       (0, 0, 0)]
                amap = [255, 255, 255, 0]
            else:
                pal = [(r0, g0, b0), (r1, g1, b1),
                       ((r0+r1)//2, (g0+g1)//2, (b0+b1)//2), (0, 0, 0)]
                amap = [255, 255, 255, 0]
            for py in range(4):
                for px in range(4):
                    k = py * 4 + px
                    j = (idx >> (2 * k)) & 3
                    Y, X = by * 4 + py, bx * 4 + px
                    rgb[Y, X] = pal[j]
                    alpha[Y, X] = amap[j]
    return rgb, alpha


if __name__ == '__main__':
    # self-test: encode a small image and decode it back
    h = w = 16
    a = np.zeros((h, w), np.uint8)
    a[2:14, 2:14] = 255
    rgb = np.zeros((h, w, 3), np.uint8)
    rgb[a > 0] = (175, 175, 175)
    enc = dxt1_encode(rgb, a)
    assert len(enc) == (w // 4) * (h // 4) * 8, len(enc)
    d_rgb, d_a = dxt1_decode(enc, w, h)
    print('encoded %d bytes for %dx%d' % (len(enc), w, h))
    print('opaque pixels: src %d  decoded %d' % (int((a > 0).sum()), int((d_a > 0).sum())))
    print('ink colour: src %s  decoded %s' % (tuple(rgb[8, 8]), tuple(d_rgb[8, 8])))
    assert int((d_a > 0).sum()) == int((a > 0).sum()), 'opacity mismatch'
    print('self-test OK')
