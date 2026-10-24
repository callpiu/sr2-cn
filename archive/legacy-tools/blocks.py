import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
W = r"F:\sr2-cn"
v = Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc"))
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
# 直接在 ASCII 区（y 0..70）找出所有字形块的包围盒，按 x 排序
band = al[0:60, :] > 32
cols = band.any(axis=0)
# 找连续列块
blocks=[]; inb=False
for x in range(2048):
    if cols[x] and not inb: inb=True; st=x
    elif not cols[x] and inb: inb=False; blocks.append((st,x-1))
if inb: blocks.append((st,2047))
print("ASCII 区（y 0..60）检测到 %d 个横向字形块" % len(blocks))
print("前 30 个块的 x 范围:")
for i,(a,b) in enumerate(blocks[:30]):
    print("  #%-3d x %4d..%4d (宽 %d)" % (i,a,b,b-a+1))
print()
print("块间距（相邻块起点差）:", [blocks[i+1][0]-blocks[i][0] for i in range(min(25,len(blocks)-1))])
print()
# 与 vf3 的 U 对照
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
N = struct.unpack_from("<i",vf3,0x08)[0]
U0 = 0xD0+N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
print("vf3 前 30 个 U 值:", U[:30])
print("块起点        :", [a for a,b in blocks[:30]])
