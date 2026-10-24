# -*- coding: utf-8 -*-
# 用**正确的**引擎取格值重新检验：L（引擎内部表）是什么排序？
# 精确实测（来自用户两轮读数 + 图集 +5 确证）：
#   E(c) = charlist.index(c) - 5   （正常字）
#   E(们)=357  E(护)=2337          （异常，多 30 / 1152）
import sys
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}
OFF = 5

CON = {"你": 366, "的": 1831, "兄": 417, "弟": 1030, "需": 2662,
       "要": 2291, "保": 386, "们": 357, "护": 2337}

print("=== 正常字：E = B序 - 5 ===")
for c, E in CON.items():
    exp = bidx[c] - OFF
    print("  %s B序=%-5d E=%-5d 应有=%-5d %s" % (c, bidx[c], E, exp, "OK" if E == exp else "★异常"))

# 假设 L = B 按某规则排序，E(c) = c 在 L 中的名次
# 对正常字：L[E(c)] == c，即 L[366]=你 L[1831]=的 L[417]=兄 L[1030]=弟 L[2662]=需 L[2291]=要 L[386]=保
print("\n=== 若 L 是排序表，已知锚点 ===")
anchors = [(E, c) for c, E in CON.items() if E == bidx[c] - OFF]
for e, c in sorted(anchors):
    print("  L[%d] = %s" % (e, c))
print("  们/护 不在锚点中（异常）")

# 检验 L = B 按 GBK 排序（B 去掉前5项后按 GBK）
try:
    cand = B[OFF:]
    gbk = sorted(cand, key=lambda c: (c.encode("gbk"), ord(c)))
    hit = sum(1 for c, E in CON.items() if E < len(gbk) and gbk[E] == c)
    print("\nL = B[5:] 按 GBK 排序：命中 %d/%d" % (hit, len(CON)))
    for c, E in CON.items():
        got = gbk[E] if E < len(gbk) else "OOB"
        if got != c:
            print("   %s 期望 L[%d]=%s 实际=%s" % (c, E, c, got))
except Exception as ex:
    print("GBK 失败:", ex)

# L = B[5:] 原序（即 B 去掉前5项）
print("\nL = B[5:] 原序（等价于图集偏移被引擎补偿）:")
for c, E in CON.items():
    got = B[E + OFF] if E + OFF < len(B) else "OOB"
    print("   %s 取格%d -> 图集显示 %s" % (c, E, got))

# 关键：们/护 若在 L=B[5:] 中，名次应为 B序-5=327/1185，但实测 357/2337
print("\n=== 们/护 在 L=B[5:] 中的名次 vs 实测 ===")
for c, E in (("们", 357), ("护", 2337)):
    print("  %s: L名次=%d  实测E=%d  差%+d" % (c, bidx[c] - OFF, E, E - (bidx[c] - OFF)))
# 差 30 / 1152 -> 若 L 去掉了 们/护 前面的一些字，名次会后移
# 检查：L=B[5:] 中，B序327..357 之间有哪些字，去掉多少个能凑成 30？
seg = B[327:357]
print("\nB[327:357] 共 %d 字: %s" % (len(seg), "".join(seg)))
seg2 = B[1185:2337]
print("B[1185:2337] 共 %d 字（护的偏移区段）" % len(seg2))
