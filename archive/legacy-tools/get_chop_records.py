import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
d = bytes(v.read(v.find("static_CH","le_strings")))
b,c,off_at,offs = file_offsets(d)
print("=== 含 map_mp_bor_chopshop 的记录（完整）===")
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    u,_ = read_units(d, off+8)
    if u is None: continue
    vals = [x for x,_ in u]
    t = "".join(S.get(x,"·") for x in vals)
    if "map_mp_bor_chopshop" in t:
        print()
        print("  记录 @%d" % off)
        print("    长度: %d 槽位 (%d 字节)" % (len(vals), len(vals)*2))
        print("    文本: %s" % t)
        print("    槽位: %s" % vals)
        # 找 img 标记的位置
        i = t.find("<img")
        j = t.find(">", i)
        print("    img 标记: %r  位置 %d..%d" % (t[i:j+1], i, j))
        print("    槽位范围: %s" % vals[i:j+1])
