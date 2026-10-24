import os, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
H1, H2 = 0x84F287ED, 0x10AF1E62
cands = [f for f in sorted(os.listdir(G)) if f.startswith("patch.vpp_pc") and f.endswith(".bak")]
cands += ["patch.vpp_pc"]
print("%-52s %-12s %s" % ("文件", "大小", "REC1 / REC2 内容"))
for fn in cands:
    p = os.path.join(G, fn)
    if not os.path.exists(p): continue
    try:
        v = Vpp(p)
    except Exception as ex:
        print("  %-50s 打不开" % fn); continue
    cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    S = {i+0x20: chr(cp) for i,cp in enumerate(cn)}
    d = bytes(v.read(v.find("static_CH","le_strings")))
    b,c,oa,offs = file_offsets(d)
    got = {}
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        cd = []
        for base in (0,4):
            for endian in ("<",">"):
                if off+base+4 > len(d): continue
                v0, = struct.unpack_from(endian+"H", d, off+base)
                v1, = struct.unpack_from(endian+"H", d, off+base+2)
                cd += [(v0<<16)|v1, (v1<<16)|v0]
        h = H1 if H1 in cd else (H2 if H2 in cd else None)
        if h is None: continue
        u,_ = read_units(d, off+8)
        got[h] = "".join(S.get(x,"·") for x,_ in u)[:32]
    print("  %-50s %-12d" % (fn, os.path.getsize(p)))
    print("      REC1: %s" % got.get(H1, "?"))
    print("      REC2: %s" % got.get(H2, "?"))
