import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
M = os.path.join(G,"Mods")
CPS = set(int(l) for l in Vpp(G+r"\patch.vpp_pc").read(Vpp(G+r"\patch.vpp_pc").find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit())
print("第三方字表 %d 项" % len(CPS))
print()
FILES = ["pause_menu.lua","main_menu.lua","sui_main_menu.lua","hud.lua","city_load.lua"]
alls = {}
for fn in FILES:
    p = os.path.join(M,fn)
    if not os.path.exists(p): continue
    b = open(p,"rb").read()
    try: t = b.decode("gbk")
    except UnicodeDecodeError as e:
        print("  %-24s GBK 解码失败: %s" % (fn,e)); continue
    cjk = sorted({c for c in t if ord(c) > 0x100})
    miss = [c for c in cjk if ord(c) not in CPS]
    alls[fn] = cjk
    print("  %-24s CJK %3d 个, 缺字形 %d 个 %s" % (fn, len(cjk), len(miss), "".join(miss) if miss else "OK"))
print()
u = set()
for v in alls.values(): u |= set(v)
miss = sorted(c for c in u if ord(c) not in CPS)
print("全部 CJK 合计 %d 个，缺字形 %d 个: %s" % (len(u), len(miss), "".join(miss) if miss else "无"))
