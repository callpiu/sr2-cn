import sys, os, struct
import numpy as np
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
W = r"F:\sr2-cn"
from sr2lib import Vpp, dxt3_decode
v0 = Vpp(os.path.join(W,"pristine","patch.vpp_pc"))
_, al0 = dxt3_decode(bytes(v0.read(v0.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
A3 = np.frombuffer(open(os.path.join(W,"_juice_fix","fnt_chinese.g_peg_pc"),"rb").read(), np.uint8).reshape(2048,2048)

print("=== 原厂 alpha 通道的值分布（16 个 DXT3 alpha 级别）===")
vals, cnts = np.unique(al0, return_counts=True)
for v,c in zip(vals, cnts): print("  %3d : %d" % (v,c))
print()
print("=== 尝试：原厂 alpha 量化为 16 级 ===")
q = (al0 // 17) * 17
print("  量化后与原厂相同: %s" % np.array_equal(q, al0))
print()
# 关键测试：把原厂按 2x2 或 4x4 下采样，看能否匹配第三方的统计
print("=== 第三方 vs 原厂 的统计对比 ===")
print("  第三方: mean %.2f  std %.2f  >32 占比 %.1f%%" % (A3.mean(), A3.std(), 100*(A3>32).mean()))
print("  原厂  : mean %.2f  std %.2f  >32 占比 %.1f%%" % (al0.mean(), al0.std(), 100*(al0>32).mean()))
print()
# 逐块相关性：取 ASCII 行 0 第 3 格
for (x,y,tag) in ((63,1,"格2"),(1427,1,"I的U")):
    o = al0[y:y+28, x:x+31].ravel().astype(float)
    t = A3[y:y+28, x:x+31].ravel().astype(float)
    if o.std()>0 and t.std()>0:
        print("  %s 原厂/第三方 相关系数 %.3f" % (tag, np.corrcoef(o,t)[0,1]))
    else:
        print("  %s 有一方为常数" % tag)
print()
print("=== 第三方图集是否可能是原厂图集的某个变换？===")
# 试：原厂非零处 第三方值 vs 原厂值
m = al0 > 0
print("  在原厂>0 的 %d 个像素上，第三方 mean=%.1f max=%d" % (m.sum(), A3[m].mean(), A3[m].max()))
m2 = al0 == 0
print("  在原厂=0 的 %d 个像素上，第三方 mean=%.1f 非零占比 %.1f%%" % (m2.sum(), A3[m2].mean(), 100*(A3[m2]>0).mean()))
