import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
W = r"F:\sr2-cn"
from sr2lib import Vpp, dxt3_decode
v0 = Vpp(os.path.join(W,"pristine","patch.vpp_pc"))
_, al0 = dxt3_decode(bytes(v0.read(v0.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
b0 = bytes(v0.read(v0.find("fnt_chinese","vf3_pc")))
A3 = np.frombuffer(open(os.path.join(W,"_juice_fix","fnt_chinese.g_peg_pc"),"rb").read(), np.uint8).reshape(2048,2048)

def load(b, off_mask):
    N = struct.unpack_from("<i",b,0x08)[0]
    CH0 = off_mask[0] + struct.unpack_from("<i",b,0x20)[0]*12
    U0 = CH0+N*16
    U = list(struct.unpack_from("<%di"%N, b, U0))
    nV = (len(b)-(U0+N*4))//4
    V = list(struct.unpack_from("<%di"%nV, b, U0+N*4))
    Wd = [struct.unpack_from("<h", b, CH0+i*16)[0] for i in range(N)]
    return N,U,V,Wd
b3 = open(os.path.join(W,"_juice_fix","fnt_chinese.vf3_pc"),"rb").read()
N3,U3,V3,W3 = load(b3,(0xD0,))
N0,U0,V0,W0 = load(b0,(0xD0,))
# 第三方 charlist
raw = open(os.path.join(W,"_juice_fix","charlist_CH.txt"),"rb").read().decode("utf-8")
cp3 = [int(l) for l in raw.split("\n") if l.strip().isdigit()]
# 原厂 charlist
from sr2lib import parse_charlist
cp0 = parse_charlist(v0.read(v0.find("charlist_CH","txt")))

def show(cps, U, V, Wd, A, chs, path, scale=5, box=30):
    tiles=[]
    for ch in chs:
        if ord(ch) not in cps:
            tiles.append(np.zeros((box,box),np.uint8)); tiles.append(np.zeros((box,3),np.uint8)); continue
        i = cps.index(ord(ch))
        x,y = U[i], V[i]
        c = A[y:y+box, x:x+box] if (0<=x<2048 and 0<=y<2048) else np.zeros((box,box),np.uint8)
        if c.shape != (box,box):
            pad=np.zeros((box,box),np.uint8); pad[:c.shape[0],:c.shape[1]]=c; c=pad
        tiles.append(c); tiles.append(np.zeros((box,3),np.uint8))
    s=np.concatenate(tiles,axis=1)
    Image.fromarray(255-s).resize((s.shape[1]*scale,s.shape[0]*scale),Image.NEAREST).save(path)
    return s

CHS = "你好中文测试黑道圣徒"
s3 = show(cp3,U3,V3,W3,A3,CHS, os.path.join(W,"_juice_fix","cjk_third.png"))
s0 = show(cp0,U0,V0,W0,al0,CHS, os.path.join(W,"_juice_fix","cjk_orig.png"))
gap=np.full((8, s3.shape[1]),128,np.uint8)
Image.fromarray(np.concatenate([s0,gap,s3],axis=0)).resize((s3.shape[1]*5, (s0.shape[0]*2+8)*5), Image.NEAREST).save(os.path.join(W,"_juice_fix","cjk_cmp.png"))
print("上=原厂（你好中文测试黑道圣徒） 下=第三方（同字）")
print("原厂墨量: %s" % [int((s0[:,i*33:(i+1)*33-3]>32).sum()) for i in range(len(CHS))])
print("第三方墨量: %s" % [int((s3[:,i*33:(i+1)*33-3]>32).sum()) for i in range(len(CHS))])
