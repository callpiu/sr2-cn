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
print("前 20 项码点:", [hex(c) for c in CPS[:20]])
print("cell 检查: (U,V)/31 →")
for i in range(0,8):
    print("  idx%-3d U=%-5d(%5.2f) V=%-5d(%5.2f)" % (i,U[i],U[i]/31,V[i],V[i]/31))
# ASCII 0..94 → 应显示 " !\"#$%&'()*+,-./0123456789:;<=>?@ABC..."
tiles=[]
for i in range(32, 96):
    x,y=U[i],V[i]
    g=al[y:y+31, x:x+31]
    tiles.append(255-g); tiles.append(np.full((31,1),160,np.uint8))
s=np.concatenate(tiles,axis=1)
Image.fromarray(s).save(r"F:/sr2-cn/_juice_fix/ascii_base.png")
print("写出 ascii_base.png: idx32..95 (应为 'A'..'~' 附近)")
