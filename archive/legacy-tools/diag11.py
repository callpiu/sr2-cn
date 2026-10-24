# -*- coding: utf-8 -*-
# 假设: 引擎用另一张字表 L 查字形 -> 验证 L[屏idx]==真字 对哪张表成立
import struct, sys, glob
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = Vpp(G + r"\patch.vpp_pc")
CPS = [int(l) for l in vp.read(vp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]

# 收集所有字表
lists = {"charlist_CH": CPS}
for f in glob.glob(G + r"\*.vpp_pc"):
    try:
        v2 = Vpp(f)
    except Exception:
        continue
    for e in v2.entries():
        if "charlist" in e['name'].lower():
            cps = [int(l) for l in v2.read(e).decode("utf-8","ignore").split("\n") if l.strip().isdigit()]
            if len(cps) > 100:
                lists[e['name']] = cps

# 用户精确转写: 真字 -> 屏幕字 (取两记录共现一致的对)
pairs = [("你","任",371,336), ("的","璨",1836,1784), ("弟","偶",1035,410),
         ("兄","巧",422,967), ("们","位",332,362), ("保","伪",391,354),
         ("护","该",1190,2342), ("他","亡",324,301), ("击","冰",479,458),
         ("去","勾",581,535), ("生","携",1792,1292), ("笔","乱",1963,287)]

for lname, L in lists.items():
    ok = 0; tot = 0; details = []
    for a, b, ia, ib in pairs:
        # L[屏idx] == 真字 ?
        hit = ib < len(L) and L[ib] == ord(a)
        ok += hit; tot += 1
        details.append(f"{a}@{ib}:{'Y' if hit else 'n'}")
    print(f"{lname} (N={len(L)}): {ok}/{tot}  {' '.join(details)}")
