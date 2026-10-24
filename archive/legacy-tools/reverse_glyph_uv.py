# -*- coding: utf-8 -*-
"""用 UV 坐标反推：正确的字形索引应该是什么。

已知
    槽位 [437, 994, 390, 1488, 2311, 562]
    屏幕显示 [使, 發, 光, 彈, 借, 步]
    charlist_CH[437-0x20] = 兄  （但屏幕不是兄）

U/V 表布局（推断）
    图集 2048×2048，字形 31×31 网格（W=29 + 间距 2 = 31）
    每行 2048/31 ≈ 66 列
    U = 列 * 31  ... 或 列 * 31 + 偏移
    V = 行 * 31
"""
import os
import struct
import sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

with LightVpp(os.path.join(G, "patch.vpp_pc")) as v:
    vf3 = None
    for e in v.entries():
        if v.name(e) == "fnt_chinese" and v.ext(e) == "vf3_pc":
            vf3 = v.read(e)
            break

N = 2838
BASE = 0xD0
recs_end = BASE + N * 16
U = [struct.unpack_from("<i", vf3, recs_end + i * 4)[0] for i in range(N)]
V = []
for i in range(N):
    o = recs_end + N * 4 + i * 4
    if o + 4 > len(vf3):
        V.append(-1)
    else:
        V.append(struct.unpack_from("<i", vf3, o)[0])

# 统计 U/V 的分布
us = sorted(set(U))
vs = sorted(set(V))
print("U 取值范围: %d .. %d  (%d 个不同值)" % (min(U), max(U), len(us)))
print("V 取值范围: %d .. %d  (%d 个不同值)" % (min(V), max(V), len(vs)))
print()

# 猜步距
if len(us) > 2:
    ds = sorted(set(us[i+1] - us[i] for i in range(len(us)-1)))
    print("U 相邻差值: %s" % ds[:12])
if len(vs) > 2:
    dv = sorted(set(vs[i+1] - vs[i] for i in range(len(vs)-1)))
    print("V 相邻差值: %s" % dv[:12])
print()

# 槽位表
SLOTS = [437, 994, 390, 1488, 2311, 562]
SHOWN = "使發光彈借步"

with LightVpp(os.path.join(G, "patch.vpp_pc")) as v2:
    for e in v2.entries():
        if v2.name(e) == "charlist_CH":
            cn = [int(l) for l in v2.read(e).decode("utf-8", "replace").split("\n")
                  if l.strip().isdigit()]
            break
CH = {i: chr(cp) for i, cp in enumerate(cn)}
IDX = {chr(cp): i for i, cp in enumerate(cn)}

print("=" * 76)
print("槽位的 UV 坐标")
print("=" * 76)
print("  %-6s %-8s %-6s %-6s %-8s %s" % ("槽位", "-0x20", "U", "V", "charlist[槽位-0x20]", "屏幕"))
for s in SLOTS:
    i = s - 0x20
    print("  %-6d %-8d %-6d %-6d %-8s %s" %
          (s, i, U[i], V[i], CH.get(i, "?"), ""))
print()

# 反推：屏幕字「使」在 charlist 的索引是 336。
# 找到一个索引 i，使 U[i]/V[i] 与 U[437] 匹配？
print("=" * 76)
print("反推：哪个索引的字形 == 屏幕显示的字？")
print("=" * 76)
for k, sh in enumerate(SHOWN):
    s = SLOTS[k]
    idx_screen = IDX.get(sh, -1)
    idx_expect = s - 0x20          # charlist 索引
    print("  槽位 %-5d: 屏幕 %s (charlist idx %d)   期望字 charlist idx %d" %
          (s, sh, idx_screen, idx_expect))
    if idx_screen >= 0:
        print("       屏幕字字形的 UV: U=%d V=%d" % (U[idx_screen], V[idx_screen]))
        print("       槽位-0x20 的 UV: U=%d V=%d" % (U[idx_expect], V[idx_expect]))
        print("       槽位本身的 UV:   U=%d V=%d" % (U[s] if s < N else -1, V[s] if s < N else -1))
    print()

# 关键检验：屏幕字的 UV 是否等于「槽位」的 UV？
print("=" * 76)
print("检验：屏幕字的字形 UV == 槽位索引的 UV ?")
print("=" * 76)
hit = 0
for k, sh in enumerate(SHOWN):
    s = SLOTS[k]
    isc = IDX.get(sh, -1)
    if isc < 0 or s >= N:
        continue
    same = (U[isc] == U[s] and V[isc] == V[s])
    if same:
        hit += 1
    print("  槽位 %-5d: 屏幕 %s(idx %-5d) UV=(%d,%d)   槽位UV=(%d,%d)  %s" %
          (s, sh, isc, U[isc], V[isc], U[s], V[s], "✓ 相同!" if same else "✗"))
print("  命中 %d/%d" % (hit, len(SHOWN)))
