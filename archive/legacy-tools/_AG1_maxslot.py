# -*- coding: utf-8 -*-
import sys, struct, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

def parse_plain(d):
    body = d.split(b'//ENDOFFILE')[0]
    return [int(x) for x in re.findall(rb'\d+', body)]

A = Vpp(r"F:\sr2-cn\_patchsrc\patch.vpp_pc")
cl = parse_plain(A.read(A.find("charlist_CH", "txt")))
print("author charlist count =", len(cl))
raw = A.read(A.find("static_CH", "le_strings"))

# walk all records via bucket table
buck = struct.unpack_from('<H', raw, 6)[0]
cnt = struct.unpack_from('<I', raw, 8)[0]
maxslot = 0
hist = {}
bad = 0
tot = 0
for b in range(buck):
    c, off = struct.unpack_from('<II', raw, 0x0C + b*8)
    o = off
    for _ in range(c):
        # each record: hash(4) + slots + 0x0000
        h = struct.unpack_from('>I', raw, o)[0]
        o += 4
        while True:
            v = struct.unpack_from('>H', raw, o)[0]; o += 2
            if v == 0:
                break
            tot += 1
            if v >= 0x100:
                if v > maxslot:
                    maxslot = v
                if v > len(cl):
                    bad += 1
                hist[v] = hist.get(v, 0) + 1
print("records=%d  total slots=%d  max slot=%d  slots>charlist_count=%d" % (cnt, tot, maxslot, bad))
print("charlist count =", len(cl))
top = sorted(hist.items(), key=lambda x: -x[1])[:15]
print("most frequent slots:", top)
