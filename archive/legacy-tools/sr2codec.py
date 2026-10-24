"""SR2 .le_strings codec.

Verified facts (empirically established against juiced_CH.cxt / juiced_CH.le_strings
which ship the same strings in plaintext and binary form):

  * File header: u32 magic 0xA84C7F73, u16 version, u16 bucketCount, u32 pairCount,
    u32 <padding/reserved>; then bucketCount * 8 bytes of buckets, then the
    pair/offset array.
  * String records live in a block of null-terminated 16-bit units.
  * Encoding of one 16-bit unit:
      - value < 0x100                 -> the ASCII/Latin-1 character itself
      - value >= 0x100                -> an INDEX into charlist_<LANG>
        (written big-endian in the string, i.e. byte0=high, byte1=low)
  * charlist_CH lives inside patch.vpp_pc as a text file: first line = count,
    then one decimal code point per line.  Slot i holds BODY[i].
"""
import struct, re, os, sys

MAGIC = 0xA84C7F73

# ---------------------------------------------------------------- charlist
class CharList:
    def __init__(self, body):
        self.body = body
        self.rev = {}
        for i, cp in enumerate(body):
            self.rev.setdefault(cp, i)

    @classmethod
    def from_vpp(cls, vpp_path, offset, size):
        V = open(vpp_path, 'rb').read()
        m = re.match(rb'(?:[0-9]+\r\n)+', V[offset:offset + size + 64])
        if not m:
            raise ValueError('charlist not found in vpp')
        nums = [int(x) for x in m.group().split()]
        body = nums[1:] if nums[0] == len(nums) - 1 else nums
        return cls(body)

    def text_to_units(self, text):
        """Encode text -> list of 16-bit units, or None if a char is unmappable."""
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

    def units_to_text(self, units):
        out = []
        for u in units:
            if u < 0x100:
                out.append(chr(u))
            elif u < len(self.body):
                out.append(chr(self.body[u]))
            else:
                return None
        return ''.join(out)

# ---------------------------------------------------------------- file access
class StringsFile:
    def __init__(self, path):
        self.path = path
        self.data = bytearray(open(path, 'rb').read())
        magic, ver, buckets, count = struct.unpack_from('<IHHI', self.data, 0)
        if magic != MAGIC:
            raise ValueError('bad magic %08X' % magic)
        self.magic, self.ver, self.buckets, self.count = magic, ver, buckets, count

    def offset_table_pos(self):
        return 0x10 + self.buckets * 8
