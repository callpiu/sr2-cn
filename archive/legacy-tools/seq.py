import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
# 目标：律(idx 1057). 打印它前后若干项的 (U,V)，并抠图
print("=== 索引 1050..1075 的 (U,V) 与字 ===")
for i in range(1050, 1076):
    print("  idx %-5d %-3s U=%-5d V=%-5d  行%d 列%d" % (
        i, chr(CPS[i]), U[i], V[i], V[i]//31, U[i]//31))
print()
# 抠出 idx 1050..1075 连续 26 个字形（用各自 U/V）
tiles=[]
for i in range(1050, 1076):
    x,y = U[i], V[i]
    g = al[y:y+28, x:x+31]
    if g.shape != (28,31):
        pad=np.zeros((28,31),np.uint8); pad[:g.shape[0],:g.shape[1]]=g; g=pad
    tiles.append(g); tiles.append(np.zeros((28,1),np.uint8))
s=np.concatenate(tiles,axis=1)
Image.fromarray(255-s).resize((s.shape[1]*6, s.shape[0]*6), Image.NEAREST).save(r"F:\sr2-cn\_juice_fix\seq1050.png")
print("写出 seq1050.png（索引 1050..1075 连续 26 字）")
print("应该依次是: %s" % "".join(chr(CPS[i]) for i in range(1050,1076)))
