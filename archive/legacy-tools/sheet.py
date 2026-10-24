import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
W = r"F:\sr2-cn"
from sr2lib import Vpp, dxt3_decode
v0 = Vpp(os.path.join(W,"pristine","patch.vpp_pc"))
_, al0 = dxt3_decode(bytes(v0.read(v0.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
A3 = np.frombuffer(open(os.path.join(W,"_juice_fix","fnt_chinese.g_peg_pc"),"rb").read(), np.uint8).reshape(2048,2048)
b0 = bytes(v0.read(v0.find("fnt_chinese","vf3_pc")))
b3 = open(os.path.join(W,"_juice_fix","fnt_chinese.vf3_pc"),"rb").read()
def load(b):
    N = struct.unpack_from("<i",b,0x08)[0]
    CH0 = 0xD0; U0 = CH0+N*16
    U = list(struct.unpack_from("<%di"%N, b, U0))
    nV = (len(b)-(U0+N*4))//4
    V = list(struct.unpack_from("<%di"%nV, b, U0+N*4))
    return N,U,V
N0,U0,V0 = load(b0); N3,U3,V3 = load(b3)

# 95 个 ASCII (索引0..94) 排成 19x5 网格，每格 34x34
def sheet(U,V,A,n=95,box=34,cols=19):
    rows = (n+cols-1)//cols
    img = np.zeros((rows*box, cols*box), np.uint8)
    for i in range(n):
        r,c = divmod(i, cols)
        x,y = U[i], V[i]
        if not (0<=x<2048 and 0<=y<2048): continue
        t = A[y:y+box, x:x+box]
        img[r*box:r*box+t.shape[0], c*box:c*box+t.shape[1]] = t
    return img
s0 = sheet(U0,V0,al0)
s3 = sheet(U3,V3,A3)
gap = np.full((8, s0.shape[1]), 128, np.uint8)
combo = np.concatenate([s0, gap, s3], axis=0)
Image.fromarray(255-combo).resize((combo.shape[1]*3, combo.shape[0]*3), Image.NEAREST).save(os.path.join(W,"_juice_fix","ascii_sheet.png"))
print("写出 ascii_sheet.png  (%dx%d, 3x)" % (combo.shape[1], combo.shape[0]))
print("上 5 行 = 原厂 95 个 ASCII ；下 5 行 = 第三方 95 个 ASCII")
