import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4)) + [0]*(N-nV)
print("V 数组补齐后 %d 项" % len(V))
print()
# 律(idx 1057) 的网格；它在行 16 列 22
# 抠出行 16（V=497）第 10..40 列，对应索引？
row = 497
idxs = [i for i in range(N) if V[i] == row]
print("行 V=497 的索引数: %d, 范围 %d..%d" % (len(idxs), idxs[0], idxs[-1]))
print("  这些索引的字符: %s" % "".join(chr(CPS[i]) for i in idxs[:40]))
print()
# 抠图：行 16 从列 10 到列 40
tiles=[]
for c in range(10, 41):
    x = 1 + 31*c
    g = al[row:row+28, x:x+31]
    tiles.append(g); tiles.append(np.zeros((28,1),np.uint8))
s=np.concatenate(tiles,axis=1)
Image.fromarray(255-s).resize((s.shape[1]*7,s.shape[0]*7),Image.NEAREST).save(r"F:\sr2-cn\_juice_fix\row16.png")
print("写出 row16.png（列 10..40）")
print("  列10 对应索引 %s" % (idxs[0] if idxs else "-"))
# 逐列标注索引
for c in range(10, 41):
    x = 1+31*c
    # 找哪个索引的 U 等于 x
    m = [i for i in range(N) if U[i] == x and V[i] == row]
    if m:
        i = m[0]
        print("    列%2d x=%4d -> idx %-5d %s" % (c, x, i, chr(CPS[i])))
