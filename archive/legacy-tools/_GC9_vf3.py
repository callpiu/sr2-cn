# -*- coding: utf-8 -*-
"""GC9: 扫描全游戏所有 *.vf3_pc, 用它们的 U/V 表去解释观测到的 (槽位->格子)。

观测(高置信, 来自截图):
   slot -> cell
   371  -> 336     你->任
   1836 -> 1784    的->璨
   1035 -> 410     弟->偶
   422  -> 967     兄->巧
   332  -> 362     们->位
   2296 -> 2268    要->衡
   391  -> 354     保->伪
   1190 -> 2342    护->该
"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OBS = [(371,336),(1836,1784),(1035,410),(422,967),(332,362),(2296,2268),(391,354),(1190,2342)]

def parse_vf3(b):
    if len(b) < 0xC0: return None
    N = struct.unpack_from("<I", b, 8)[0]
    if N <= 0 or N > 100000: return None
    uoff = 0xBC + 16*N
    voff = uoff + 4*N
    if voff + 4*N > len(b): return None
    U = struct.unpack_from("<%dI"%N, b, uoff)
    V = struct.unpack_from("<%dI"%N, b, voff)
    return N, U, V

def cell_of(U, V, i):
    if i >= len(U): return None
    u, v = U[i], V[i]
    if u == 0 or v == 0: return None
    col = (u-1)//31; row = (v-1)//31
    return row*65 + col

results = []
for fn in sorted(os.listdir(G)):
    if not fn.lower().endswith(".vpp_pc"): continue
    p = os.path.join(G, fn)
    try: v = Vpp(p)
    except Exception: continue
    for e in v.entries():
        k = e['name'] + ('.'+e['ext'] if e['ext'] else '')
        if not k.endswith(".vf3_pc"): continue
        b = v.read(e)
        r = parse_vf3(b)
        if not r: continue
        N, U, V = r
        hits = sum(1 for s, j in OBS if cell_of(U, V, s) == j)
        results.append((hits, fn, k, N, len(b)))

results.sort(reverse=True)
print("%-4s %-18s %-28s %6s %9s" % ("命中", "vpp", "vf3", "N", "size"))
for h, fn, k, N, sz in results[:25]:
    print("%-4d %-18s %-28s %6d %9d" % (h, fn, k, N, sz))

# 对命中最高者, 打印逐项
if results:
    h, fn, k, N, sz = results[0]
    print("\n--- 最优: %s / %s  N=%d ---" % (fn, k, N))
    v = Vpp(os.path.join(G, fn))
    for e in v.entries():
        kk = e['name'] + ('.'+e['ext'] if e['ext'] else '')
        if kk == k:
            N2, U, V = parse_vf3(v.read(e))
            for s, j in OBS:
                print("   slot %5d -> cell %s  (期望 %d)" % (s, cell_of(U, V, s), j))
            break
