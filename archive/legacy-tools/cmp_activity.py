import os, sys, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
H1, H2 = 0x84F287ED, 0x10AF1E62
def show(lab, p):
    if not os.path.exists(p): print("%s 不存在" % lab); return
    v = Vpp(p)
    cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    S = {i+0x20: chr(cp) for i,cp in enumerate(cn)}
    d = bytes(v.read(v.find("static_CH","le_strings")))
    b,c,oa,offs = file_offsets(d)
    print("=== %s (%d 项, static_CH %d 字节) ===" % (lab, len(cn), len(d)))
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        if off+4 > len(d): continue
        h = struct.unpack_from("<I", d, off)[0]
        if h not in (H1,H2): continue
        u,end = read_units(d, off+8)
        if u is None: continue
        vals = [x for x,_ in u]
        t = "".join(S.get(x,"\uFFFD") for x in vals)
        print("  hash 0x%08X @%-9d 头: %s" % (h, off, d[off:off+8].hex(" ")))
        print("    %s" % t)
        print("    槽位: %s" % vals)
    print()
for lab, p in (("当前部署", os.path.join(G,"patch.vpp_pc")),
               ("v533_tagfix", os.path.join(G,"patch.vpp_pc.v533_tagfix_20261012_131656.bak")),
               ("v532_clean", os.path.join(G,"patch.vpp_pc.v532_before_exp.bak")),
               ("v531_before_mirror", os.path.join(G,"patch.vpp_pc.v531_before_mirror.bak"))):
    show(lab, p)
