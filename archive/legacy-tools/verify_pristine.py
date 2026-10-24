# -*- coding: utf-8 -*-
"""原厂自洽性: 原厂vf3 + 原厂图集 + 原厂表 -> 渲染是否 cell p = 表[p]"""
import os, sys, struct, re
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode

v0 = Vpp(r"F:/sr2-cn/pristine/patch.vpp_pc")
# 原厂图集
atl = dxt3_decode(bytes(v0.read(v0.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)[1]
# 原厂 vf3
vf3 = bytes(v0.read(v0.find("fnt_chinese", "vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N * 16
U = list(struct.unpack_from("<%di" % N, vf3, U0))
nV = (len(vf3) - (U0 + N * 4)) // 4
V = list(struct.unpack_from("<%di" % nV, vf3, U0 + N * 4)) + [0] * (N - nV)
# 原厂表(跳过前面垃圾数字: 只取 >=32 起? 用原始顺序)
buf = v0.read(v0.find("charlist_CH", "txt"))
end = buf.find(b'//ENDOFFILE')
raw = [int(x) for x in re.findall(rb'\d+', buf[:end])]
print("raw 前16:", raw[:16])
# 官方表真实起点: 找到 32 开始
start = raw.index(32)
real = raw[start:]  # 但后面可能还有非字符数字
print("start idx=%d real前16=%s" % (start, real[:16]))
print("real 长度=%d" % len(real))

tbl = real
def tl(i, w):
    x, y = U[i], V[i]
    g = atl[y:y + 30, x:x + w]
    return g

# 渲染 cell 0..24, 宽度用 19(原厂步长)
w = U[1] - U[0]
print("原厂步长 U[1]-U[0]=", w)
ts = []
for p in range(0, 26):
    g = atl[V[p]:V[p] + 30, U[p]:U[p] + w]
    if g.shape != (30, w):
        q = np.zeros((30, w), np.uint8); q[:g.shape[0], :g.shape[1]] = g; g = q
    ts.append(g); ts.append(np.full((30, 1), 200, np.uint8))
s = np.concatenate(ts, axis=1)
Image.fromarray(255 - s).resize((s.shape[1] * 8, s.shape[0] * 8), Image.NEAREST).save(r"F:/sr2-cn/_pristine_cells.png")
print("原厂 cell0..25 -> _pristine_cells.png")
print("若 cell p = real[p], 前26应为:", [chr(c) if c < 128 else hex(c) for c in real[:26]])
