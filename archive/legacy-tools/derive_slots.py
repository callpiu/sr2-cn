# -*- coding: utf-8 -*-
"""当场从 VPP 字表推导 slot 值，并据此重建搜索。"""
import sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
cps = [int(l) for l in
       v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]

print("字表 %d 项" % len(cps))
slot_of = {}
for i, cp in enumerate(cps):
    slot_of.setdefault(cp, i + 0x20)

want = "辩护律师延师三丈王老斯蒂尔沃特郊区"
print("\n### 当场推导 slot（slot = idx + 0x20）")
for ch in want:
    cp = ord(ch)
    if cp in slot_of:
        print("  %s U+%04X -> idx %5d -> slot %5d (0x%04X)"
              % (ch, cp, slot_of[cp] - 0x20, slot_of[cp], slot_of[cp]))
    else:
        print("  %s U+%04X -> 不在字表中 !!" % (ch, cp))

# 反查：确认若干 slot 到底对应哪个字
print("\n### 反查我此前使用的 slot 值")
for s in [2506, 1222, 1089, 1057, 1013, 271, 270, 1796, 1379, 2254, 952, 1601, 1773]:
    idx = s - 0x20
    ch = chr(cps[idx]) if 0 <= idx < len(cps) else None
    print("  slot %5d -> idx %5d -> %r" % (s, idx, ch))

print("\n### 相邻 slot 邻域（看是否 238/239、1057/1089 有近邻混淆）")
for center in [270, 1089]:
    row = []
    for s in range(center - 4, center + 5):
        idx = s - 0x20
        row.append("%d:%r" % (s, chr(cps[idx]) if 0 <= idx < len(cps) else None))
    print("  %s" % "  ".join(row))

print("\n### 在 VPP 内 static_CH 找 '辩护' 全部条目（当场解码，不依赖记忆）")
sc = bytes(v.read(v.find("static_CH", "le_strings")))
TS = 16 + 0
# 用现成解析器
sys.path.insert(0, r"F:\sr2-cn")
from sr2patch import file_offsets, read_units
b, c, off_at, offs = file_offsets(sc)
print("  buckets=%d count=%d TS=%d" % (b, c, 16 + b * 8 + c * 4 + 4))
hits = 0
for off in offs:
    r = read_units(sc, off + 8)
    if not r:
        continue
    slots = [x for x, _ in r[0]]
    if not slots:
        continue
    txt = "".join(chr(cps[s - 0x20]) if 0 <= s - 0x20 < len(cps) else "<?%d>" % s
                  for s in slots)
    if "辩护" in txt or "三王" in txt or "丈王" in txt:
        print("   @%-8d %r  slots=%s" % (off, txt, slots))
        hits += 1
print("  命中 %d 条" % hits)