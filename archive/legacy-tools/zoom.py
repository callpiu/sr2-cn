import sys, os, struct
import numpy as np
from PIL import Image
W = r"F:\sr2-cn"
A = np.frombuffer(open(os.path.join(W,"_juice_fix","fnt_chinese.g_peg_pc"),"rb").read(), np.uint8).reshape(2048,2048)
# 把顶部 130 行整条放大看
top = A[0:130, 0:700]
Image.fromarray(255-top).resize((700*2, 130*2), Image.NEAREST).save(os.path.join(W,"_juice_fix","top_zoom.png"))
print("写出 top_zoom.png (0:130 行, 0:700 列, 2x)")
# 找每行非零像素
cnt = (A>0).sum(axis=1)
for y in range(0, 70):
    marks = np.nonzero(A[y]>0)[0]
    if len(marks):
        print("y=%3d  非零 %4d  首 %4d 末 %4d" % (y, len(marks), marks.min(), marks.max()))
    else:
        print("y=%3d  空行" % y)
