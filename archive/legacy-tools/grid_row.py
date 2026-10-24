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
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
# 用「网格坐标」而不是 U/V：索引 i -> 行 = V[i]//31, 列 = U[i]//31
# 打印 idx 1057(律) 与 idx 1339(文) 的网格坐标
for ch in "律文":
    i = CPS.index(ord(ch))
    print("  %s idx %d: U=%d V=%d -> 行 %d 列 %d (格号 %d)" % (
        ch, i, U[i], V[i], V[i]//31, U[i]//31, (V[i]//31)*66 + U[i]//31))
print()
# 直接按行打印图集第 16 行（V≈497）与第 20 行（V≈621）的前 46 格
for row, vv in ((16, 497), (20, 621)):
    tiles=[]
    for c in range(46):
        x = 1 + 31*c
        g = al[vv:vv+28, x:x+31]
        if g.shape != (28,31):
            pad=np.zeros((28,31),np.uint8); pad[:g.shape[0],:g.shape[1]]=g; g=pad
        tiles.append(g); tiles.append(np.zeros((28,1),np.uint8))
    s=np.concatenate(tiles,axis=1)
    Image.fromarray(255-s).resize((s.shape[1]*5,s.shape[0]*5),Image.NEAREST).save(r"F:\sr2-cn\_juice_fix\row%d.png" % row)
    # 该行对应的索引范围
    idxs = [i for i in range(N) if V[i]//31 == row]
    print("  行 %d (V=%d): 索引 %s .. %s, 字符 %s" % (
        row, vv, idxs[0] if idxs else "-", idxs[-1] if idxs else "-",
        "".join(chr(CPS[i]) for i in idxs[:46])))
    print("     写出 row%d.png" % row)
