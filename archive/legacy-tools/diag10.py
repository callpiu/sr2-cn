# -*- coding: utf-8 -*-
# 验证「码点二分回退」假设：bisect(CPS, slot值) 的落点是否 = 屏幕错字 idx
import struct, sys, bisect
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = Vpp(G + r"\patch.vpp_pc")
CPS = [int(l) for l in vp.read(vp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
idx_of = {}
for i, c in enumerate(CPS):
    idx_of.setdefault(c, i)

# slot值 -> 屏幕字 (用户精确转写)
obs = [
    (0x193, "任"), (0x74c, "璨"), (0x42b, "偶"), (0x1c6, "巧"), (0x16c, "位"),
    (0xa8b, "雄"), (0x918, "衡"), (0x1a7, "伪"), (0x4c6, "该"),
    (0x1fe, "校"), (0x265, "衡"), (0x955, "勾"), (0x1f6, "远"),
    (0x7cb, "藐"), (0x720, "乱"), (0x487, "携"),
    (0xb06, "亡"), (0x164, "通"), (0x1cc, "像"), (0xa03, "匪"), (0x908, "冰"),
]
# 注: 0x265(去)用户写勾; 0x918(要)在REC2写校/REC1写衡 -> 以REC2为准两组都试
print(f"{'slot':>6} {'bisect左':>8} {'CPS[落点]':>8} | {'屏幕字':>4} {'屏idx':>6} | 落点==屏idx?")
for v, gch in obs:
    j = bisect.bisect_left(CPS, v)
    gi = idx_of.get(ord(gch))
    cj = chr(CPS[j]) if j < len(CPS) else '?'
    mark = "YES <<<" if gi is not None and j == gi else ""
    print(f"0x{v:04X} {j:>8} {cj:>8} | {gch}  {gi!s:>6} | {mark}")
