# -*- coding: utf-8 -*-
# 计算渲染偏移：真字idx vs 截图乱码字idx，找恒定delta
import struct, sys
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
sys.stdout.reconfigure(encoding="utf-8")

V531 = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc.v531_before_mirror.bak"
vpp = Vpp(V531)
CPS = [int(l) for l in vpp.read(vpp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
N = len(CPS)
idx_of = {}
for i, c in enumerate(CPS):
    idx_of.setdefault(c, i)

# 截图乱码（记录1=0x84F287ED 前8字 + 记录2=0x10AF1E62 全部）
# 记录1 slot: 你0x193 的0x74c 弟0x42b 兄0x1c6 们0x16c 需0xa8b 要0x918 保0x1a7 护0x4c6
# 截图记录1: 任 璨 傅 巧 位 衡 ... 伪 该 (对应 你的弟兄们?需要..保护)
# 记录2 slot: 你0x193 的0x74c 弟0x42b 兄0x1c6 们0x16c 要0x918 出0x1fe 去0x265 谈0x955 几0x1f6
#             笔0x7cb 生0x720 意0x487 ，0xb06 保0x1a7 护0x4c6 他0x164 们0x16c 免0x1cc 遭0xa03 袭0x908 击0x1ff
# 截图记录2: 任 璨 傅 巧 位 校 衡 勾 远 覫 乱 携 (意?) 伪 该 亡 位 遗 像 匪 冰 挺 拮
pairs = [
    ("你", "任"), ("的", "璨"), ("弟", "傅"), ("兄", "巧"), ("们", "位"),
    ("要", "校"), ("出", "衡"), ("去", "勾"), ("谈", "远"), ("几", "覫"),
    ("笔", "乱"), ("生", "携"),
    ("保", "伪"), ("护", "该"), ("他", "亡"), ("免", "遗"), ("遭", "像"),
    ("袭", "匪"), ("击", "冰"),
]
print(f"{'真字':>4} {'真idx':>6} {'屏字':>4} {'屏idx':>6} {'delta':>6}")
for a, b in pairs:
    ia, ib = idx_of.get(ord(a)), idx_of.get(ord(b))
    d = (ib - ia) if (ia is not None and ib is not None) else None
    print(f"{a}(U+{ord(a):04X}) {ia!s:>6} {b}(U+{ord(b):04X}) {ib!s:>6} {d!s:>6}")

# 附加：已知坏字位台账对照（会->伙 等）
print("\n已知坏字位台账验证:")
for a, b in [("律", "延"), ("三", "丈"), ("必", "弗"), ("心", "引"), ("得", "开"), ("联", "伙"), ("会", "伙")]:
    ia, ib = idx_of.get(ord(a)), idx_of.get(ord(b))
    print(f"  {a} idx={ia} -> {b} idx={ib} delta={None if None in (ia,ib) else ib-ia}")
