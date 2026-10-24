import sys, os, struct
import numpy as np
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
W = r"F:\sr2-cn"
A3 = np.frombuffer(open(os.path.join(W,"_juice_fix","fnt_chinese.g_peg_pc"),"rb").read(), np.uint8).reshape(2048,2048)
print("=== 第三方图集像素统计 ===")
for v in (0,16,32,64,128,192,255):
    print("  值 %3d : %d 像素" % (v, int((A3==v).sum())))
vals, cnts = np.unique(A3, return_counts=True)
print("  不同灰度值 %d 个" % len(vals))
top = sorted(zip(cnts, vals), reverse=True)[:10]
print("  最常见: %s" % [(int(v), int(c)) for c,v in top])
print()
from sr2lib import Vpp, dxt3_decode
v0 = Vpp(os.path.join(W,"pristine","patch.vpp_pc"))
raw0 = bytes(v0.read(v0.find("fnt_chinese","g_peg_pc")))
_, al0 = dxt3_decode(raw0, 2048, 2048)
print("=== 原厂图集（DXT3 解出的 alpha 单通道）===")
print("  形状 %s dtype %s" % (al0.shape, al0.dtype))
for v in (0,16,32,64,128,192,255):
    print("  值 %3d : %d 像素" % (v, int((al0==v).sum())))
vals0, cnts0 = np.unique(al0, return_counts=True)
print("  不同灰度值 %d 个" % len(vals0))
top0 = sorted(zip(cnts0, vals0), reverse=True)[:10]
print("  最常见: %s" % [(int(v), int(c)) for c,v in top0])
