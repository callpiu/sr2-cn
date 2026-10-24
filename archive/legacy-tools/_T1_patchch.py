# -*- coding: utf-8 -*-
import sys, struct, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
P = GAME + r"\mods\JUICED - Strings\patch_ch.le_strings"
raw = open(P, 'rb').read()
print("len", len(raw), "head", raw[:24].hex(' '))
magic = struct.unpack_from('<I', raw, 0)[0]
ver = struct.unpack_from('<H', raw, 4)[0]
buck = struct.unpack_from('<H', raw, 6)[0]
cnt = struct.unpack_from('<I', raw, 8)[0]
print("magic %08x ver %d buckets %d count %d" % (magic, ver, buck, cnt))

# table from 0x0C: (count u32, offset u32)
tbl = []
for i in range(buck):
    c, o = struct.unpack_from('<II', raw, 0x0C + i * 8)
    tbl.append((c, o))
print("first buckets:", tbl[:4], "sum", sum(c for c, _ in tbl))
tot = 0
for name, pat in (('F284ED87', b'\xf2\x84\xed\x87'), ('5A5AA49A', b'\x5a\x5a\xa4\x9a'),
                  ('1738DE48', b'\x17\x38\xde\x48')):
    i = raw.find(pat)
    print(name, "at", i, raw[i:i+60].hex(' ') if i >= 0 else '')
