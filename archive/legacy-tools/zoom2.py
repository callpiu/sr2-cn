import sys, os, struct
import numpy as np
from PIL import Image
W = r"F:\sr2-cn"
A = np.frombuffer(open(os.path.join(W,"_juice_fix","fnt_chinese.g_peg_pc"),"rb").read(), np.uint8).reshape(2048,2048)
# 用 U/V 表定位
b = open(os.path.join(W,"_juice_fix","fnt_chinese.vf3_pc"),"rb").read()
N = struct.unpack_from("<i",b,0x08)[0]
CH0 = 0xD0; U0 = CH0+N*16
U = list(struct.unpack_from("<%di"%N, b, U0))
nV = (len(b)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, b, U0+N*4))
# 把 'J'(42) 'U'(53) 'I'(41) 单独放大看
tiles=[]
for ch in "JUICED":
    i = ord(ch)-32
    x,y = U[i], V[i]
    c = A[y:y+34, x:x+34]
    if c.shape != (34,34):
        pad=np.zeros((34,34),np.uint8); pad[:c.shape[0],:c.shape[1]]=c; c=pad
    tiles.append(c); tiles.append(np.zeros((34,2),np.uint8))
s = np.concatenate(tiles, axis=1)
Image.fromarray(255-s).resize((s.shape[1]*10, s.shape[0]*10), Image.NEAREST).save(os.path.join(W,"_juice_fix","JUICED_zoom.png"))
print("写出 JUICED_zoom.png")
for ch in "JUICED":
    i = ord(ch)-32
    x,y = U[i], V[i]
    c = A[y:y+34, x:x+34]
    print("%s 索引%3d (U=%4d,V=%3d) 墨量=%4d  行非零=%s" % (
        ch, i, x, y, int((c>32).sum()), [int((c[r]>32).sum()) for r in range(0,30,3)]))
# 对照：第 3 个 ASCII 行带（y=68）里的 CJK，看是否正常
print()
print("=== 对比：y=68 附近的字形（应是中文）===")
cnt = (A>0).sum(axis=1)
print("  y=68..95 各行非零数: %s" % [int(cnt[y]) for y in range(68,96,3)])
