import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
W = r"F:\sr2-cn"
v = Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc"))
d = bytes(v.read(v.find("fnt_chinese","g_peg_pc")))
print("原始 %d 字节" % len(d))
# 找第一个非零字节
nz = next((i for i,b in enumerate(d) if b), None)
print("第一个非零字节位置: %s" % nz)
print("前 80 字节: %s" % d[:80].hex(' '))
print()
# 统计前 4096 字节里非零的个数
pre = d[:4096]
print("前 4096 字节非零: %d (%.1f%%)" % ((np.frombuffer(pre,np.uint8)>0).sum(), 100*(np.frombuffer(pre,np.uint8)>0).mean()))
print("全文件非零: %.1f%%" % (100*(np.frombuffer(d,np.uint8)>0).mean()))
print()
# 试各种偏移做 DXT3 解码
for off in (0, 16, 32, 48, 64, 80, 128):
    dd = d[off:off+4194304]
    if len(dd) < 4194304: 
        print("  偏移 %3d: 数据不足" % off); continue
    try:
        rgb, al = dxt3_decode(dd, 2048, 2048)
        inked = (al>32)
        # 量 ASCII 区（行 0..90）的清晰度：用边缘密度
        strip = al[0:90, :]
        e = np.abs(np.diff(strip.astype(int), axis=0)).sum() + np.abs(np.diff(strip.astype(int), axis=1)).sum()
        print("  偏移 %3d: 非零 %.1f%%  边缘量 %8d" % (off, 100*inked.mean(), e))
        if off in (0,16,32,48,64):
            Image.fromarray(255-al[0:94, 0:2048]).save(os.path.join(W,"_juice_fix","dxt3_off%d.png"%off))
    except Exception as ex:
        print("  偏移 %3d: 解码失败 %s" % (off, ex))
