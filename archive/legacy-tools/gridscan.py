import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS=[int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N=struct.unpack_from("<i",vf3,0x08)[0]
CELL=31
rows=2048//CELL; cols=2048//CELL
print("网格 %dx%d cell=%d" % (rows,cols,CELL))
# 扫第0行前12格
print("图集第0行前14格:")
for c in range(14):
    y0,x0 = 0*CELL, c*CELL
    g=al[y0:y0+CELL, x0:x0+CELL]
    print("   列%-3d (%4d,%4d) 墨量=%d" % (c, x0, y0, int((g>32).sum())))
# U/V 数组第0..10项 vs 网格
U0=0xD0+N*16
U=list(struct.unpack_from("<%di"%N,vf3,U0))
nV=(len(vf3)-(U0+N*4))//4
V=list(struct.unpack_from("<%di"%nV,vf3,U0+N*4))
print("\nU/V[0..10] 与网格坐标:")
for i in range(11):
    x,y=U[i],V[i]
    print("   idx%-3d U=%-5d(列%.2f) V=%-5d(行%.2f)" % (i,x,x/CELL,y,y/CELL))
