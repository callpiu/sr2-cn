"""SR2 Traditional -> Simplified Chinese patcher.

Encoding facts, all verified empirically:

  .le_strings layout
    u32 magic 0xA84C7F73 | u16 version=1 | u16 bucketCount | u32 pairCount
    bucketCount * 8 bytes of buckets
    pairCount  * 4 bytes of absolute file offsets
    records:  u64 hash, then a 0x0000-terminated stream of 16-bit units

  unit -> character
    value < 0x100     : the character itself
    value >= 0x100    : charlist[value - 0x20]        <-- the -0x20 shift

  charlist_CH (text file inside patch.vpp_pc): first line = count, then one
  decimal code point per line.

Because Traditional -> Simplified is character-for-character, the patch is done
as an IN-PLACE substitution of the "slot" units: every record keeps exactly the
same number of units, so all offsets, hashes and file sizes stay valid and the
file layout is completely untouched.
"""
import re, struct, sys, os, collections

MAGIC = 0xA84C7F73
# Verified mapping:  character = body[slot - SHIFT],  slot = body index + SHIFT
# (`body` is the parsed charlist entry list; the file itself also carries SHIFT
#  leading space entries, which is why the shift appears twice in places.)
SHIFT = 0x20
HDR = 16

# ---------------------------------------------------------------- charlist
class CharList:
    def __init__(self, body):
        self.body = list(body)
        self.rev = {}
        for i, cp in enumerate(self.body):
            self.rev.setdefault(cp, i)
        # slot the game expects for each character (slot = body index + SHIFT)
        self.rev32 = {cp: i + SHIFT for i, cp in enumerate(self.body)}
        for i, cp in enumerate(self.body):
            self.rev32.setdefault(cp, i + SHIFT)

    @classmethod
    def from_vpp_text(cls, text):
        nums = [int(x) for x in text.split()]
        body = nums[1:] if nums and nums[0] == len(nums) - 1 else nums
        return cls(body)

    def char(self, slot):
        idx = slot - SHIFT
        if 0 <= idx < len(self.body):
            return chr(self.body[idx])
        return None

    def slot(self, ch):
        """slot value the game expects for a character"""
        cp = ord(ch)
        if cp < 0x100:
            return cp
        if cp in self.rev:
            return self.rev[cp] + SHIFT
        return None

    def to_file_text(self):
        """Serialise exactly like the original file.

        The original charlist file already begins with SHIFT spaces as its first
        entries, i.e. the *file index* is `body index + SHIFT`, and the game maps
        `character = file[slot - SHIFT]`.  Writing the body out unchanged keeps
        that identity true after every character we append.
        """
        parts = [str(len(self.body))]
        parts += [str(cp) for cp in self.body]
        return ('\r\n'.join(parts) + '\r\n//ENDOFFILE\r\n\x00').encode('ascii') + (
            b"//Used character list based on file "
            b"'d:\\projects\\sr2\\main\\data\\tables\\charlist_CH.txt'\r\n\x00")


# ---------------------------------------------------------------- unit IO
def read_units(d, start):
    """-> (list_of_slots, end_index_of_terminator). Slots are the raw 16-bit BE values."""
    n = len(d)
    i = start
    us = []
    while i + 2 <= n:
        b0, b1 = d[i], d[i + 1]
        if b0 == 0 and b1 == 0:
            return us, i + 2
        us.append(((b0 << 8) | b1, i))   # value, byte position
        i += 2
    return None, None


def decode(units, cl):
    out = []
    for v, pos in units:
        if v < 0x100:
            out.append(chr(v))
        else:
            c = cl.char(v)
            if c is None:
                return None
            out.append(c)
    return ''.join(out)


def file_offsets(d):
    n = len(d)
    magic, ver, buckets, count = struct.unpack_from('<IHHI', d, 0)
    assert magic == MAGIC
    off_at = HDR + buckets * 8
    offs = [struct.unpack_from('<I', d, off_at + k * 4)[0] for k in range(count)]
    return buckets, count, off_at, offs


def all_texts(path, cl):
    d = open(path, 'rb').read()
    buckets, count, off_at, offs = file_offsets(d)
    res = []
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d) - 10):
            continue
        units, end = read_units(d, off + 8)
        if units is None:
            continue
        t = decode(units, cl)
        if t is not None:
            res.append((off, units, t))
    return d, res
