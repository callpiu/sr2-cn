# -*- coding: utf-8 -*-
"""交叉验证：作者图集 65 列布局下 cell 336 = 任。
   在官方繁体图集里找"哪一格最像它"。若 = 371 ⇒ 提示行用的是官方图集。"""
import os, sys, numpy as np
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode

G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
PR = r"F:/sr2-cn/pristine/patch.vpp_pc"

def cell(alpha, idx, W, x0, y0, p=31, s=31):
    c, r = idx % W, idx // W
    x, y = x0 + p*c, y0 + p*r
    return alpha[y:y+s, x:x+s].astype(np.float32)

def norm(a):
    a = a - a.mean()
    n = np.linalg.norm(a)
    return a / n if n > 1e-6 else a

def sim(a, b):
    return float((norm(a) * norm(b)).sum())

# 作者图集 (patch)
cn = Vpp(os.path.join(G, "patch.vpp_pc"))
ab = cn.read(cn.find("fnt_chinese", "g_peg_pc"))
_, aA = dxt3_decode(ab, 2048, 2048)
print("作者图集解码完成")

# 官方图集 (pristine)
pv = Vpp(PR)
ob = pv.read(pv.find("fnt_chinese", "g_peg_pc"))
_, oA = dxt3_decode(ob, 2048, 2048)
print("官方图集解码完成")

# 参考：作者 cell 336 (65列) = 任
ref = cell(aA, 336, 65, 1, 1)
print("作者 cell336 非零像素:", int((ref > 20).sum()))

# 在官方图集里找最相似的格子（试 66 列与 65 列两种布局）
for W, x0, y0, tag in ((66, 0, 0, "官方66列 x0=0"), (66, 1, 1, "官方66列 x0=1"),
                       (65, 1, 1, "官方65列 x0=1")):
    scores = []
    for i in range(2838):
        c, r = i % W, i // W
        x, y = x0 + 31*c, y0 + 31*r
        if y + 31 > 2048 or x + 31 > 2048: break
        scores.append((sim(ref, oA[y:y+31, x:x+31].astype(np.float32)), i))
    scores.sort(reverse=True)
    print(f"  [{tag}] top5: " + ", ".join(f"idx{i}={s:.3f}" for s, i in scores[:5]))

# 反向：作者 cell 371(你) 在官方图集里的最佳匹配
ref2 = cell(aA, 371, 65, 1, 1)
for W, x0, y0, tag in ((66, 0, 0, "官方66列 x0=0"), (66, 1, 1, "官方66列 x0=1")):
    scores = []
    for i in range(2838):
        c, r = i % W, i // W
        x, y = x0 + 31*c, y0 + 31*r
        if y + 31 > 2048 or x + 31 > 2048: break
        scores.append((sim(ref2, oA[y:y+31, x:x+31].astype(np.float32)), i))
    scores.sort(reverse=True)
    print(f"  [你 {tag}] top5: " + ", ".join(f"idx{i}={s:.3f}" for s, i in scores[:5]))
