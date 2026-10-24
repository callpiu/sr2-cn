import os, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
H1, H2 = 0x84F287ED, 0x10AF1E62
v = Vpp(os.path.join(G,"patch.vpp_pc"))
d = bytes(v.read(v.find("static_CH","le_strings")))
b,c,oa,offs = file_offsets(d)
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    cands = []
    for base in (0,4):
        for endian in ("<",">"):
            if off+base+4 > len(d): continue
            v0, = struct.unpack_from(endian+"H", d, off+base)
            v1, = struct.unpack_from(endian+"H", d, off+base+2)
            cands += [(v0<<16)|v1, (v1<<16)|v0]
    h = H1 if H1 in cands else (H2 if H2 in cands else None)
    if h is None: continue
    u,_ = read_units(d, off+8)
    print("  hash 0x%08X -> %r" % (h, "".join(chr(x) for x,_ in u)))
