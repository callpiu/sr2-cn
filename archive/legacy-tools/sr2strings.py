"""SR2 .le_strings reader/writer - verified layout."""
import struct

MAGIC = 0xA84C7F73
HDR = 16          # magic(4) + version(2) + bucketCount(2) + pairCount(4) + reserved(4)


class CharList:
    def __init__(self, body):
        self.body = list(body)
        self.rev = {}
        for i, cp in enumerate(self.body):
            self.rev.setdefault(cp, i)

    @classmethod
    def from_text(cls, text):
        nums = [int(x) for x in text.split()]
        body = nums[1:] if nums and nums[0] == len(nums) - 1 else nums
        return cls(body)

    def to_text(self):
        parts = [str(len(self.body))] + [str(cp) for cp in self.body]
        return '\r\n'.join(parts) + '\r\n//ENDOFFILE\r\n\x00'

    def encode(self, text):
        out = []
        for ch in text:
            cp = ord(ch)
            if cp < 0x100:
                out.append(cp)
            elif cp in self.rev:
                out.append(self.rev[cp])
            else:
                return None
        return out

    def decode(self, units):
        out = []
        for u in units:
            if u < 0x100:
                out.append(chr(u))
            elif u < len(self.body):
                out.append(chr(self.body[u]))
            else:
                return None
        return ''.join(out)


class StringsFile:
    def __init__(self, path=None, data=None):
        self.path = path
        self.data = bytearray(data if data is not None else open(path, 'rb').read())
        magic, ver, buckets, count = struct.unpack_from('<IHHI', self.data, 0)
        assert magic == MAGIC, hex(magic)
        self.ver, self.buckets, self.count = ver, buckets, count
        self.offsets_at = HDR + buckets * 8

    # ---- offsets -----------------------------------------------------
    def offsets(self):
        d = self.data
        return [struct.unpack_from('<I', d, self.offsets_at + i * 4)[0]
                for i in range(self.count)]

    def set_offset(self, i, value):
        struct.pack_into('<I', self.data, self.offsets_at + i * 4, value)

    # ---- records -----------------------------------------------------
    def read_record(self, off):
        """-> (hash8, unitcount, units[list of u16])"""
        d, n = self.data, len(self.data)
        if not (0 <= off <= n - 12):
            return None
        L = struct.unpack_from('<I', d, off + 8)[0]
        base = off + 12
        if not (0 <= L <= 20000) or base + L * 2 + 2 > n:
            return None
        if d[base + L * 2: base + L * 2 + 2] != b'\x00\x00':
            return None
        raw = d[base: base + L * 2]
        units = []
        for k in range(L):
            b0, b1 = raw[2 * k], raw[2 * k + 1]
            units.append(b1 if b0 == 0 else ((b0 << 8) | b1))
        return bytes(d[off:off + 8]), L, units

    def decode(self, charlist, off):
        r = self.read_record(off)
        if r is None:
            return None
        return charlist.decode(r[2])

    def encode_units(self, charlist, text):
        units = charlist.encode(text)
        if units is None:
            return None
        raw = bytearray()
        for u in units:
            raw += bytes((0, u)) if u < 0x100 else bytes(((u >> 8) & 0xFF, u & 0xFF))
        return bytes(raw)

    def all_records(self, charlist):
        """-> list of (index, offset, text, unitcount) for the distinct offsets"""
        seen = {}
        out = []
        for i, off in enumerate(self.offsets()):
            if off in seen:
                continue
            seen[off] = i
            r = self.read_record(off)
            if r is None:
                continue
            t = charlist.decode(r[2])
            if t is None:
                continue
            out.append((i, off, t, r[1]))
        return out
