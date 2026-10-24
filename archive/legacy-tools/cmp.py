import sys, os
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
W = r"F:\sr2-cn"
from sr2lib import Vpp, dxt3_decode
v0 = Vpp(os.path.join(W,"pristine","patch.vpp_pc"))
_, al0 = dxt3_decode(bytes(v0.read(v0.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
A3 = np.frombuffer(open(os.path.join(W,"_juice_fix","fnt_chinese.g_peg_pc"),"rb").read(), np.uint8).reshape(2048,2048)

# 原厂 ASCII 行 0..2 共 3 个带，每带 31px -> 0..93
o = 255 - al0[0:94, 0:2048]
t = 255 - A3[0:94, 0:2048]
# 上下拼接并放大 1x（宽度已 2048）
gap = np.full((6, 2048), 128, np.uint8)
combo = np.concatenate([o, gap, t], axis=0)
Image.fromarray(combo).save(os.path.join(W,"_juice_fix","cmp_ascii_1x.png"))
# 只取前 700 列放大 2x
combo2 = np.concatenate([o[:, :700], gap[:, :700], t[:, :700]], axis=0)
Image.fromarray(combo2).resize((1400, combo2.shape[0]*2), Image.NEAREST).save(os.path.join(W,"_juice_fix","cmp_ascii_zoom.png"))
print("写出 cmp_ascii_1x.png / cmp_ascii_zoom.png")
print("上 = 原厂（繁体官方），下 = 第三方")
