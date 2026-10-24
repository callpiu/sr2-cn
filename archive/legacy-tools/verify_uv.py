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
U0=0xAF6C
NU=(0xDB18-U0)//4
U=list(struct.unpack_from("<%di"%NU, vf3, U0))
V=list(struct.unpack_from("<%di"%NU, vf3, 0xDB18))
print("N=%d  U项数=%d  V项数=%d  文件末=%d" % (N,NU,NU,len(vf3)))
print("U[0..8]=",U[:9]); print("V[0..8]=",V[:9])
tiles=[]
for i in range(0,45):
    x,y=U[i],V[i]
    g=al[y:y+31, x:x+31]
    tiles.append(255-g); tiles.append(np.full((31,1),120,np.uint8))
s=np.concatenate(tiles,axis=1)
Image.fromarray(s).save(r"F:/sr2-cn/_juice_fix/head45_fix.png")
print("写出 head45_fix.png (idx 0..44, 期望 ' '..'L')")
# 目标字
for ch,slot in [("辩",2506),("护",1222),("律",1089),("延",1057),("师",1013),("三",271),("丈",270),("王",1796)]:
    i=slot-0x20; x,y=U[i],V[i]
    print("  %s slot=%-5d idx=%-5d (%4d,%4d) 墨量=%d" % (ch,slot,i,x,y,int((al[y:y+31,x:x+31]>32).sum())))
tiles=[]
for ch,slot in [("辩",2506),("护",1222),("律",1089),("延",1057),("师",1013),("三",271),("丈",270),("王",1796)]:
    i=slot-0x20; x,y=U[i],V[i]
    tiles.append(255-al[y:y+31, x:x+31]); tiles.append(np.full((31,3),160,np.uint8))
s=np.concatenate(tiles,axis=1)
Image.fromarray(s).resize((s.shape[1]*10,s.shape[0]*10),Image.NEAREST).save(r"F:/sr2-cn/_juice_fix/target_fix.png")
