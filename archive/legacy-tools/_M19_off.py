# -*- coding: utf-8 -*-
# 算图集实际字形 vs charlist 的索引偏移，找规律
import sys
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}

# 实测：图集第 k 格显示的字（人工读图）
OBS = {332: "份", 362: "何", 1190: "抵", 2342: "说"}

print("%-6s %-8s %-8s %-8s %s" % ("格子k", "charlist", "实际字形", "码点差", "索引差"))
for k, ch in OBS.items():
    exp = B[k]
    if ch in bidx:
        print("%-6d %-8s %-8s %+8d %+8d" % (k, exp, ch, ord(ch) - ord(exp), bidx[ch] - k))
    else:
        print("%-6d %-8s %-8s %+8d %s" % (k, exp, ch, ord(ch) - ord(exp), "不在B"))

# 若偏移恒定，反推图集第 k 格 = B[k + D]
print("\n=== 检验恒定偏移 D ===")
for D in range(-40, 41):
    ok = all(B[k + D] == ch for k, ch in OBS.items() if 0 <= k + D < len(B))
    if ok:
        print("  ★ D = %d 成立！图集第 k 格 = charlist[k%+d]" % (D, D))
if not any(all(B[k + D] == ch for k, ch in OBS.items() if 0 <= k + D < len(B)) for D in range(-40, 41)):
    print("  无恒定偏移")

# 逐个看：份/何/抵/说 在 B 中的位置
print("\n=== 这些字在 charlist 中的位置 ===")
for ch in "份何抵说们位护该":
    print("  %s (U+%04X) B序 = %s" % (ch, ord(ch), bidx.get(ch, "不在")))

# 关键：引擎取格 = B.index(显示字)？重新检验
# 用户实测：们 -> 显示 位。若图集第k格 = B[k+D]，引擎取格 = B.index(源字)
# 则显示 = B[B.index(源字)+D]
print("\n=== 若引擎取格 = charlist.index(源字)，显示 = B[that + D] ===")
for D in range(-40, 41):
    ok = True
    for src, disp in (("们", "位"), ("护", "该")):
        i = bidx[src]
        if not (0 <= i + D < len(B)) or B[i + D] != disp:
            ok = False
            break
    if ok:
        print("  ★ D = %d：们->B[%d]=%s  护->B[%d]=%s" % (
            D, bidx["们"] + D, B[bidx["们"] + D], bidx["护"] + D, B[bidx["护"] + D]))
