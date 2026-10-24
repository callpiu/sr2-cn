"""列出 static_CH 里所有含「保护/弟兄/袭击」的记录（不限长度），
并标出哪些是【活动开始提示】候选。

用户描述：字幕在活动开始、过场动画结束进入操作时出现 -> 是活动开场提示。
这类文本通常较短（一句提示），但也可能较长。
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
d = bytes(v.read(v.find("static_CH", "le_strings")))
b, c, oa, offs = file_offsets(d)

KEYS = ("保护", "弟兄", "袭击")
rows = []
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d) - 10):
        continue
    u, _ = read_units(d, off + 8)
    if u is None:
        continue
    vals = [x for x, _ in u]
    t = "".join(S.get(x, "\uFFFD") for x in vals)
    if any(k in t for k in KEYS):
        rows.append((off, len(t), t))

print("共 %d 条含关键词的记录" % len(rows))
print()
print("=== 按长度排序 ===")
for off, n, t in sorted(rows, key=lambda r: r[1]):
    print("  @%-9d len=%-4d %s" % (off, n, t[:76]))
