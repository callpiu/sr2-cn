import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
W = r"F:\sr2-cn"
OUT = os.path.join(W,"_juice_fix","out","patch.vpp_pc")
v = Vpp(OUT)
A = np.frombuffer(v.read(v.find("fnt_chinese","g_peg_pc")), np.uint8).reshape(2048,2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
N = struct.unpack_from("<i",vf3,0x08)[0]; CH0 = 0xD0
U0 = CH0+N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV = (len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
def sheet(A,U,V,n=95,box=34,cols=19):
    rows=(n+cols-1)//cols
    img=np.zeros((rows*box,cols*box),np.uint8)
    for i in range(n):
        r,c=divmod(i,cols)
        x,y=U[i],V[i]
        if not(0<=x<2048 and 0<=y<2048): continue
        t=A[y:y+box, x:x+box]
        img[r*box:r*box+t.shape[0], c*box:c*box+t.shape[1]]=t
    return img
s = sheet(A,U,V)
Image.fromarray(255-s).resize((s.shape[1]*3, s.shape[0]*3), Image.NEAREST).save(os.path.join(W,"_juice_fix","ascii_fixed.png"))
print("写出 ascii_fixed.png")
# 与第三方原始对比
from sr2lib import dxt3_decode
v3 = Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc"))
A3 = np.frombuffer(v3.read(v3.find("fnt_chinese","g_peg_pc")), np.uint8).reshape(2048,2048)
s3 = sheet(A3,U,V)
# 原厂
v0 = Vpp(os.path.join(W,"pristine","patch.vpp_pc"))
_, al0 = dxt3_decode(bytes(v0.read(v0.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
b0 = bytes(v0.read(v0.find("fnt_chinese","vf3_pc")))
N0=struct.unpack_from("<i",b0,0x08)[0]; U00=0xD0+N0*16
U0_=list(struct.unpack_from("<%di"%N0,b0,U00))
nV0=(len(b0)-(U00+N0*4))//4
V0_=list(struct.unpack_from("<%di"%nV0,b0,U00+N0*4))
s0 = sheet(al0,U0_,V0_)
gap=np.full((8,s.shape[1]),128,np.uint8)
combo=np.concatenate([s0,gap,s3,gap,s],axis=0)
Image.fromarray(255-combo).resize((combo.shape[1]*3, combo.shape[0]*3), Image.NEAREST).save(os.path.join(W,"_juice_fix","ascii_3way.png"))
print("写出 ascii_3way.png  上=原厂  中=第三方(坏)  下=修复后")
