"""列出 static_CH 里所有可能作为「活动字幕」的记录。

用户看到的乱码有 22 个字，内容疑似是「弟兄们要出去谈几笔生意，保护他们免遭袭击」
（REC2）。但改了 REC2 也没生效。

所以可能：
  (a) 有第三条记录也含类似文本，屏幕用的是它
  (b) 屏幕用的根本不是 static_CH

本脚本列出所有「短记录且含关键词」的条目，供人工核对。
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(G, "patch.vpp_pc")

v = Vpp(SRC)
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
d = bytes(v.read(v.find("static_CH", "le_strings")))
b, c, oa, offs = file_offsets(d)
print("static_CH: %d 记录" % len(set(offs)))

KEYS = ["保护", "弟兄", "袭击", "生意"]
rows = []
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d) - 10):
        continue
    u, end = read_units(d, off + 8)
    if u is None:
        continue
    vals = [x for x, _ in u]
    t = "".join(S.get(x, "\uFFFD") for x in vals)
    if any(k in t for k in KEYS) and len(t) <= 70:
        rows.append((off, len(vals), t, vals))

print()
print("=== 含关键词的短记录（共 %d 条）===" % len(rows))
for off, n, t, vals in rows:
    print("  @%-9d len=%-4d %s" % (off, n, t))
print()
print("=== 前 16 槽位对照 ===")
for off, n, t, vals in rows:
    print("  @%-9d %s" % (off, vals[:16]))
