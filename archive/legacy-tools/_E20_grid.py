# -*- coding: utf-8 -*-
"""★★★ 根因锁定：两张图集的网格不同，而 common.vf3 与 textures 图集不匹配

事实（u32 正确读取）：
  patch  vf3:  U 步长 = 31 (1,32,63,...)      V 行距 = 31 (1,32,63,94,...)
  common vf3:  U 步长 = 18（行0）/ 13+30（行1+） V 行距 = 31 (1,32,63,...)
               V[224..232] = 63  ← 注意是 63 不是 32！

  ★ patch  U 步长 31 = 图集格宽 31  ⇒ 与【汉化图集】网格一致
  ★ common U 步长 18/13/30 ≠ 31    ⇒ 与【官方图集】网格不一致

但要确认【官方图集】的网格步长。方法：找图集中字形墨迹的列间距。
"""
import sys, os, struct
import numpy as np
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load(path):
    v = Vpp(path); e = v.find("fnt_chinese", "vf3_pc"); o = v.data_start + e['body']
    N = struct.unpack_from('<I', v.data, o + 8)[0]
    ro = 0xBC; uo = ro + N*16; vo = uo + N*4
    U = [struct.unpack_from('<I', v.data, o+uo+i*4)[0] for i in range(N)]
    V = [struct.unpack_from('<I', v.data, o+vo+i*4)[0] for i in range(N)]
    return U, V, N

UP, VP, NP = load(os.path.join(G, "patch.vpp_pc"))
UC, VC, NC = load(os.path.join(G, "common.vpp_pc"))

print("== U/V 散布分析 ==")
def stats(U, V, N, tag):
    print("-- %s N=%d" % (tag, N))
    print("   U 唯一值个数 %d，范围 %d..%d" % (len(set(U)), min(U), max(U)))
    print("   V 唯一值个数 %d，范围 %d..%d" % (len(set(V)), min(V), max(V)))
    su = sorted(set(U)); sv = sorted(set(V))
    du = [su[i+1]-su[i] for i in range(min(20, len(su)-1))]
    dv = [sv[i+1]-sv[i] for i in range(min(20, len(sv)-1))]
    print("   U 前20个唯一值间隔:", du)
    print("   V 前20个唯一值间隔:", dv)
    print("   U 唯一值前12:", su[:12])
    print("   V 唯一值前12:", sv[:12])
stats(UP, VP, NP, "patch")
stats(UC, VC, NC, "common")

# 直接看两张图集的实际字形列间距（墨迹投影）
print("\n== 图集实际网格 ==")
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
AH = vp.read(vp.find("fnt_chinese", "g_peg_pc"))
vt = Vpp(os.path.join(G, "textures.vpp_pc"))
AT = vt.read(next(x for x in vt.entries() if x['name'] == 'fnt_chinese'))
_, PH = dxt3_decode(AH, 2048, 2048)
_, PT = dxt3_decode(AT, 2048, 2048)
for tag, A in (("汉化图集(patch)", PH), ("官方图集(textures)", PT)):
    col = (A[:200, :] > 8).sum(axis=0)
    # 找非空列块的分界
    nz = np.where(col > 0)[0]
    print("-- %s  前40个非空列: %s" % (tag, nz[:40].tolist()))
    # 估计格距：非空列块起点
    starts = [nz[0]]
    for i in range(1, len(nz)):
        if nz[i] - nz[i-1] > 2:
            starts.append(nz[i])
    d = [starts[i+1]-starts[i] for i in range(min(15, len(starts)-1))]
    print("   列块起点间隔:", d)
