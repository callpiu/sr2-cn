import sys, os, struct
import numpy as np
W = r"F:\sr2-cn"
A = np.frombuffer(open(os.path.join(W,"_juice_fix","fnt_chinese.g_peg_pc"),"rb").read(), np.uint8).reshape(2048,2048)
b = open(os.path.join(W,"_juice_fix","fnt_chinese.vf3_pc"),"rb").read()
N = struct.unpack_from("<i",b,0x08)[0]
CH0 = 0xD0; U0 = CH0+N*16
U = list(struct.unpack_from("<%di"%N, b, U0))
nV = (len(b)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, b, U0+N*4))

# 取几个 ASCII 字母，在候选 dy 下测「落在 17x17 框内的墨量」
tests = {ch: ord(ch)-32 for ch in "JUICEDisplay"}
print("=== 各 dy 下 ASCII 字形在 17x17 框内的墨量（sum）===")
best=[]
for dy in range(-30, 40):
    tot=0
    for ch,i in tests.items():
        x, y = U[i], V[i]+dy
        if y < 0 or y+17 > 2048: continue
        tot += int((A[y:y+17, x:x+17] > 32).sum())
    best.append((tot, dy))
best.sort(reverse=True)
for tot, dy in best[:12]:
    print("  dy=%+4d  墨量合计 %6d" % (dy, tot))
print()
# 也测 dx
print("=== 各 dx 下（dy 用最优）===")
dy0 = best[0][1]
best2=[]
for dx in range(-20, 21):
    tot=0
    for ch,i in tests.items():
        x, y = U[i]+dx, V[i]+dy0
        if x < 0 or x+17 > 2048: continue
        tot += int((A[y:y+17, x:x+17] > 32).sum())
    best2.append((tot, dx))
best2.sort(reverse=True)
for tot, dx in best2[:8]:
    print("  dx=%+4d  墨量合计 %6d" % (dx, tot))
print()
print("最优: dy=%+d dx=%+d" % (best[0][1], best2[0][1]))
