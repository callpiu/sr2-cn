# -*- coding: utf-8 -*-
"""全局扫描: 图集格 i 实际绘制 = 表[i+off(i)]。用渲染+OCR? 不行。
改用: 已知 patch 表与 common 表/原厂表 的差异, 反推图集来源。
关键: fnt_chinese.g_peg_pc 图集 是从哪张表烤的?
  - 若图集来自"原厂2848表"排布 => 图集格i = 原厂表[i]
  - 那么渲染(用patch表idx i)取图集格i = 原厂表[i]，显示 = 原厂表[i]
验证: patch表[371]='你'(idx371), 图集[371]显示='使'。'使'在原厂表idx=? 
"""
import os, sys, struct, re
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
PRISTINE = r"F:/sr2-cn/pristine/patch.vpp_pc"

v = Vpp(os.path.join(G, "patch.vpp_pc"))
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese", "vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N * 16
U = list(struct.unpack_from("<%di" % N, vf3, U0))
nV = (len(vf3) - (U0 + N * 4)) // 4
V = list(struct.unpack_from("<%di" % nV, vf3, U0 + N * 4)) + [0] * (N - nV)


def load_tbl(path):
    vv = Vpp(path)
    buf = vv.read(vv.find("charlist_CH", "txt"))
    end = buf.find(b'//ENDOFFILE')
    if end < 0:
        end = len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]


patch = load_tbl(os.path.join(G, "patch.vpp_pc"))
pris = load_tbl(PRISTINE)
ps = "".join(chr(c) for c in patch)
pr = "".join(chr(c) for c in pris)
print("patch=%d pristine=%d" % (len(patch), len(pris)))
print("图集[371]='使' -> in patch@%d  in pristine@%d" % (ps.find('使'), pr.find('使')))
print("图集[336]='伎' -> in patch@%d  in pristine@%d (上面读到的是伎)" % (ps.find('伎'), pr.find('伎')))
# 关键对比: 图集格 i 用 U[i],V[i]; 若图集按 pristine 排布:
# 则 图集格i = pristine[i]. 检查 i=371 图集应显示 pristine[371]
print("pristine[371]=", chr(pris[371]))
print("pristine[336]=", chr(pris[336]))
print("patch[371]=", chr(patch[371]))
# 更大范围: 渲染 i=371 与 i=336 的图集
def tl(i):
    x, y = U[i], V[i]
    g = al[y:y + 30, x:x + 31]
    if g.shape != (30, 31):
        p = np.zeros((30, 31), np.uint8); p[:g.shape[0], :g.shape[1]] = g; g = p
    return g
import numpy as np
ts = []
for i in [371, 336, 332, 422, 1035]:
    ts.append(tl(i)); ts.append(np.full((30, 3), 255, np.uint8))
s = np.concatenate(ts, axis=1)
Image.fromarray(255 - s).resize((s.shape[1] * 8, s.shape[0] * 8), Image.NEAREST).save(r"F:/sr2-cn/_probe_garble.png")
print("写出 _probe_garble.png : 顺序 idx 371(你) 336(任) 332(们) 422(兄) 1035(弟)")
