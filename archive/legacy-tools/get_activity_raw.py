import os, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
H1, H2 = 0x84F287ED, 0x10AF1E62
for label, p in (("当前部署 build_fix", os.path.join(G,"patch.vpp_pc")),
                 ("干净 v532", os.path.join(G,"patch.vpp_pc.v532_before_exp.bak"))):
    if not os.path.exists(p): 
        print("=== %s 不存在 ===" % label); continue
    v = Vpp(p)
    CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
    d = bytes(v.read(v.find("static_CH","le_strings")))
    b,c,oa,offs = file_offsets(d)
    print("=== %s ===" % label)
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        u,end = read_units(d, off+8)
        if u is None: continue
        # read_units 返回 (value, bytepos)；记录头的 id1/id2 在 off..off+4
        id1, id2 = struct.unpack_from(">HH", d, off)
        h = (id1<<16)|id2
        if h not in (H1,H2): continue
        vals = [x for x,_ in u]
        t = "".join(S.get(x,"\uFFFD") for x in vals)
        print("  hash 0x%08X  @%-9d  len=%d" % (h, off, len(vals)))
        print("    文本: %s" % t)
        print("    槽位: %s" % vals)
        # 每个槽位对应的索引和字
        print("    槽位 -> (idx, 字): %s" % [(x, x-0x20, S.get(x,"?")) for x in vals[:16]])
        print()
