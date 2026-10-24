import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
W = r"F:\sr2-cn"
v = Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc"))
rgb, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N = struct.unpack_from("<i",vf3,0x08)[0]
U0 = 0xD0+N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
# 按索引 0..94 (即 ASCII 0x20..0x7E) 排成 19x5
cols, box = 19, 34
rows=(95+cols-1)//cols
img=np.zeros((rows*box, cols*box), np.uint8)
for i in range(95):
    r,c=divmod(i,cols)
    x,y=U[i],V[i]
    t=al[y:y+box, x:x+box]
    img[r*box:r*box+t.shape[0], c*box:c*box+t.shape[1]]=t
Image.fromarray(255-img).resize((img.shape[1]*2, img.shape[0]*2), Image.NEAREST).save(os.path.join(W,"_juice_fix","ascii_ok.png"))
print("写出 ascii_ok.png %dx%d" % (img.shape[1]*2, img.shape[0]*2))
