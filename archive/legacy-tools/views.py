import sys, os
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
W = r"F:\sr2-cn"
v = Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc"))
d = bytes(v.read(v.find("fnt_chinese","g_peg_pc")))
raw = np.frombuffer(d, np.uint8).reshape(2048,2048)
_, al = dxt3_decode(d, 2048, 2048)
# 三方图：原始字节视图 / DXT3 alpha 视图
Image.fromarray(255-raw).save(os.path.join(W,"_juice_fix","view_raw.png"))
Image.fromarray(255-al).save(os.path.join(W,"_juice_fix","view_dxt3.png"))
print("写出 view_raw.png (按原始字节) 与 view_dxt3.png (按 DXT3 解码)")
print()
# 各取 ASCII 顶部 region 放大对比
o1 = 255-raw[0:120, 0:900]
o2 = 255-al[0:120, 0:900]
gap = np.full((6, 900), 128, np.uint8)
Image.fromarray(np.concatenate([o1,gap,o2],axis=0)).resize((1800, (120*2+6)*2), Image.NEAREST).save(os.path.join(W,"_juice_fix","view_cmp.png"))
print("写出 view_cmp.png  (上=原始字节  下=DXT3解码)")
# 统计
print()
print("原始字节: 非零 %.1f%%  前 2000 字节非零 %d" % (100*(raw>0).mean(), int((raw.ravel()[:2000]>0).sum())))
print("DXT3 alpha: 非零 %.1f%%  灰度级别 %d" % (100*(al>0).mean(), len(np.unique(al))))
