import sys, os
import numpy as np
from PIL import Image
W = r"F:\sr2-cn"
def load(p):
    return np.frombuffer(open(p,"rb").read(), np.uint8).reshape(2048,2048)
third = load(os.path.join(W,"_juice_fix","fnt_chinese.g_peg_pc"))
# 第三方 ASCII 区（前 3 个行带 * 31px）
crop = third[0:100, 0:2048]
Image.fromarray(255-crop).resize((2048//2, 50), Image.NEAREST).save(os.path.join(W,"_juice_fix","ascii_third.png"))
# 原厂对照
import sys as s2
s2.path.insert(0, W)
from sr2lib import Vpp, dxt3_decode
v0 = Vpp(os.path.join(W,"pristine","patch.vpp_pc"))
at = bytes(v0.read(v0.find("fnt_chinese","g_peg_pc")))
rgb, al = dxt3_decode(at, 2048, 2048)
crop0 = al[0:100, 0:2048]
Image.fromarray(255-crop0).resize((2048//2, 50), Image.NEAREST).save(os.path.join(W,"_juice_fix","ascii_orig.png"))
print("写出 ascii_third.png / ascii_orig.png")
# 逐格打印前 95 格的墨量（按格 31px，行0）
print()
print("=== 第三方 行0 每格墨量（格 0..65）===")
for c in range(66):
    x = 1 + 31*c
    if x+31 > 2048: break
    ink = int((third[1:29, x:x+31] > 32).sum())
    print("  格%2d x=%4d ink=%4d" % (c, x, ink), end="")
    if c % 4 == 3: print()
