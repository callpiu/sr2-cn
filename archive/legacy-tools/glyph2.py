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
print("NumCharacters =", N, " 字表项数 =", len(CPS))
U0=0xD0+N*16
U=list(struct.unpack_from("<%di"%N,vf3,U0))
nV=(len(vf3)-(U0+N*4))//4
V=list(struct.unpack_from("<%di"%nV,vf3,U0+N*4))
print("V 数组长度 =", nV)
#记录 16B: +0x00/+0x0C i16 width, +0x08 i16 (-1)
def rec(i):
    return struct.unpack_from("<hhhh", vf3, 0xD0+i*16)
for slot in (1089,1057,271,270,1796,1371,2506,1222,1013):
    i=slot-0x20
    w0,_,w1,_=rec(i)
    x,y=U[i],V[i]
    print("slot %-5d idx %-5d w0=%-4d w1=%-4d U=%-5d V=%-5d" % (slot,i,w0,w1,x,y))
# 用 w0 作为宽度渲染
tiles=[]
order=[1089,1057,271,270,1796,1371]
for slot in order:
    i=slot-0x20; w0,_,w1,_=rec(i)
    x,y=U[i],V[i]
    w=max(w0,w1)+2
    g=al[y:y+36, x:x+w]
    tiles.append(255-g); tiles.append(np.full((36,6),160,np.uint8))
s=np.concatenate(tiles,axis=1)
Image.fromarray(s).resize((s.shape[1]*14,s.shape[0]*14),Image.NEAREST).save(r"F:/sr2-cn/_juice_fix/glyph_w.png")
print("顺序 slot:", order, " 尺寸", s.shape)
