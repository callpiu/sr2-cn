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
U0=0xD0+N*16
U=list(struct.unpack_from("<%di"%N,vf3,U0))
nV=(len(vf3)-(U0+N*4))//4
V=list(struct.unpack_from("<%di"%nV,vf3,U0+N*4))

print("假设：图集 idx i 画的是 charlist[i+5]")
for ch in "辩 护 律 师 三 王 文 丈 延".split():
    cp=ord(ch); ti=CPS.index(cp)
    print("  %s 字表idx=%-5d  → 若偏移+5: 需读 idx=%-5d(slot %d)" % (ch, ti, ti-5, ti-5+0x20))
print()
# 渲染偏移前后
pairs=[("律 字表idx1057",1057),("idx1052(假设=律)",1052),
       ("三 字表idx239",239),("idx234(假设=三)",234),
       ("王 字表idx1764",1764),("idx1759(假设=王)",1759),
       ("师 字表idx981",981),("idx976(假设=师)",976)]
tiles=[]
for label,i in pairs:
    x,y=U[i],V[i]
    g=al[y:y+31, x:x+31]
    print("  %-20s idx=%-5d (%4d,%4d) 墨量=%d" % (label,i,x,y,int((g>32).sum())))
    tiles.append(255-g); tiles.append(np.full((31,3),160,np.uint8))
s=np.concatenate(tiles,axis=1)
Image.fromarray(s).resize((s.shape[1]*9,s.shape[0]*9),Image.NEAREST).save(r"F:/sr2-cn/_juice_fix/offset.png")
