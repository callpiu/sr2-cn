import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
W = r"F:\sr2-cn"
def load_vf3(p):
    b = open(p,"rb").read()
    N = struct.unpack_from("<i",b,0x08)[0]
    NK = struct.unpack_from("<i",b,0x20)[0]
    CH0 = 0xD0 + NK*12
    U0 = CH0 + N*16
    U = list(struct.unpack_from("<%di"%N, b, U0))
    nV = (len(b)-(U0+N*4))//4
    V = list(struct.unpack_from("<%di"%nV, b, U0+N*4))
    WID = [struct.unpack_from("<h", b, CH0+i*16)[0] for i in range(N)]
    return b, N, U, V, WID

b3,N3,U3,V3,W3 = load_vf3(os.path.join(W,"_juice_fix","fnt_chinese.vf3_pc"))
A3 = np.frombuffer(open(os.path.join(W,"_juice_fix","fnt_chinese.g_peg_pc"),"rb").read(), np.uint8).reshape(2048,2048)
from sr2lib import Vpp, dxt3_decode
v0 = Vpp(os.path.join(W,"pristine","patch.vpp_pc"))
_, al0 = dxt3_decode(bytes(v0.read(v0.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
b0 = bytes(v0.read(v0.find("fnt_chinese","vf3_pc")))
b0,N0,U0,V0,W0 = load_vf3.__wrapped__ if False else (None,None,None,None,None)
# 手工加载原厂（V 数组少 5 项）
bb = bytes(v0.read(v0.find("fnt_chinese","vf3_pc")))
N0 = struct.unpack_from("<i",bb,0x08)[0]
CH00 = 0xD0
U00 = CH00 + N0*16
UU0 = list(struct.unpack_from("<%di"%N0, bb, U00))
nV0 = (len(bb)-(U00+N0*4))//4
VV0 = list(struct.unpack_from("<%di"%nV0, bb, U00+N0*4)) + [0]*(N0-nV0)
WW0 = [struct.unpack_from("<h", bb, CH00+i*16)[0] for i in range(N0)]

print("=== ASCII 前 12 个字符 ===")
print("%-6s %-8s %-20s %-20s" % ("字符","索引","第三方 (U,V,width)","原厂 (U,V,width)"))
for i in range(12):
    ch = chr(32+i)
    print("%-6r %-8d (%4d,%4d,%3d)      (%4d,%4d,%3d)" % (
        ch, i, U3[i], V3[i], W3[i], UU0[i], VV0[i], WW0[i]))

def strip(A, U, V, n, path, scale=6):
    imgs=[]
    for i in range(n):
        x,y = U[i], V[i]
        c = A[y:y+30, x:x+32] if (0<=x<2048 and 0<=y<2048) else np.zeros((30,32),np.uint8)
        if c.shape != (30,32):
            pad=np.zeros((30,32),np.uint8); pad[:c.shape[0],:c.shape[1]]=c; c=pad
        imgs.append(c)
    s=np.concatenate(imgs,axis=1)
    Image.fromarray(255-s).resize((s.shape[1]*scale,s.shape[0]*scale),Image.NEAREST).save(path)
    return s
s3=strip(A3,U3,V3,12,os.path.join(W,"_juice_fix","glyphs_third.png"))
s0=strip(al0,UU0,VV0,12,os.path.join(W,"_juice_fix","glyphs_orig.png"))
print()
print("第三方 12 格墨量: %s" % [int((s3[:,i*32:(i+1)*32]>32).sum()) for i in range(12)])
print("原厂   12 格墨量: %s" % [int((s0[:,i*32:(i+1)*32]>32).sum()) for i in range(12)])
# J 的位置
print()
print("=== 「JUICED」六个字母的位置 ===")
for ch in "JUICED":
    i = 32 + (ord(ch)-32) if False else ord(ch)-32
    # 第三方索引 = 码点-32（因为 charlist 从 32 连续开始）
    print("  %s: 第三方索引 %d -> (U,V)=(%d,%d) width=%d" % (ch, i, U3[i], V3[i], W3[i]))
