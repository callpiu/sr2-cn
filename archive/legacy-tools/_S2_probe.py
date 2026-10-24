# -*- coding: utf-8 -*-
import sys, struct, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(GAME + r"\patch.vpp_pc")
ent = pv.find("static_CH")
raw = pv.read(ent)
print("len", len(raw))
print("first 32:", raw[:32].hex(' '))
magic = struct.unpack_from('<I', raw, 0)[0]
ver   = struct.unpack_from('<H', raw, 4)[0]
buck  = struct.unpack_from('<H', raw, 6)[0]
cnt   = struct.unpack_from('<I', raw, 8)[0]
print("magic %08x ver %d buckets %d count %d" % (magic, ver, buck, cnt))
print("bucket table 0x10..0x50:", raw[16:0x50].hex(' '))
