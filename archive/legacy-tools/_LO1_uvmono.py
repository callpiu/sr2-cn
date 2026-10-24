# -*- coding: utf-8 -*-
# 决定性检验：vf3 的 U/V 坐标序列是否单调（图集是否按 charlist 顺序紧密打包）
# 若 们(332)/护(1190) 附近出现非单调 => 图集打包顺序与 charlist 不一致
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

f = Font(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
N = f.N
print("vf3 N =", N, " charlist =", len(f.charlist))

U = [struct.unpack_from("<i", f.vf3, f.UOFF + k * 4)[0] for k in range(N)]
V = [struct.unpack_from("<i", f.vf3, f.VOFF + k * 4)[0] for k in range((len(f.vf3)-f.VOFF)//4)]
print("U 范围 %d..%d   V 范围 %d..%d" % (min(U), max(U), min(V), max(V)))
print("U 唯一值数 =", len(set(U)), "  V 唯一值数 =", len(set(V)))

CELL = 31
BW = 2048
# 行优先：row = V/31, col = U/31 -> 线性序号 = row*64+col
NV = len(V)
lin = [(V[k] // CELL) * (BW // CELL) + (U[k] // CELL) for k in range(NV)]
bad = [k for k in range(NV - 1) if lin[k] >= lin[k + 1]]

print("\n线性序号非单调点数 =", len(bad))
print("前 50 个:", bad[:50])

# 关键位置
for ch in "们护你兄弟需要保位该":
    i = f.idx(ch)
    if i is None:
        print("  %s 不在 charlist" % ch); continue
    print("  %s  idx=%-5d U=%-5d V=%-5d lin=%-5d" % (ch, i, U[i], V[i], lin[i]))

# 每行起点（V 相同的一组）验证列是否等距
print("\n=== 前 3 行的 UV（验证网格）===")
rows = {}
for k in range(N):
    rows.setdefault(V[k] // CELL, []).append(k)
for r in sorted(rows)[:4]:
    ks = rows[r]
    us = [U[k] for k in ks]
    print("  row%d: %d 格, U = %s" % (r, len(ks), us[:14]))
