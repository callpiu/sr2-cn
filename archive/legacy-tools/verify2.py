import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
W = r"F:\sr2-cn"
def sheet_from(path, native):
    v = Vpp(path)
    if native:
        A = np.frombuffer(v.read(v.find("fnt_chinese","g_peg_pc")), np.uint8).reshape(2048,2048)
    else:
        _, A = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
    vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
    N = struct.unpack_from("<i",vf3,0x08)[0]
    U0 = 0xD0+N*16
    U = list(struct.unpack_from("<%di"%N, vf3, U0))
    nV=(len(vf3)-(U0+N*4))//4
    V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
    box, cols = 34, 19
    rows=(95+cols-1)//cols
    out=np.zeros((rows*box, cols*box), np.uint8)
    for i in range(95):
        r,c=divmod(i,cols)
        x,y=U[i],V[i]
        if not(0<=x<2048 and 0<=y<2048): continue
        t=A[y:y+box, x:x+box]
        out[r*box:r*box+t.shape[0], c*box:c*box+t.shape[1]]=t
    return out
s_before = sheet_from(os.path.join(W,"_juice_fix","patch.vpp_pc"), True)
s_after  = sheet_from(os.path.join(W,"_juice_fix","out","patch.vpp_pc"), True)
s_orig   = sheet_from(os.path.join(W,"pristine","patch.vpp_pc"), False)
# 原厂的 U/V 表不同，但 ASCII 位置一样，可对照
gap=np.full((8,s_before.shape[1]),128,np.uint8)
combo=np.concatenate([s_orig, gap, s_before, gap, s_after], axis=0)
Image.fromarray(255-combo).resize((combo.shape[1]*3, combo.shape[0]*3), Image.NEAREST).save(os.path.join(W,"_juice_fix","ascii_final_cmp.png"))
print("写出 ascii_final_cmp.png")
print("第1组=原厂  第2组=第三方(坏)  第3组=修复后")
