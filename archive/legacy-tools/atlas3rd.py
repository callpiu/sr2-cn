import sys, os, struct
import numpy as np
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
W = r"F:\sr2-cn"
a = open(os.path.join(W,"_juice_fix","fnt_chinese.g_peg_pc"),"rb").read()
print("文件 %d 字节 = 2048*2048 = %d  -> 未压缩 8bit 单通道" % (len(a), 2048*2048))
A = np.frombuffer(a, np.uint8).reshape(2048,2048)
print("min=%d max=%d mean=%.2f" % (A.min(), A.max(), A.mean()))
print("非零像素 %d (%.1f%%)" % ((A>0).sum(), 100.0*(A>0).sum()/A.size))
rows = (A>0).any(axis=1)
nz = np.nonzero(rows)[0]
print("有内容的行: %d / 2048   范围 %d..%d" % (rows.sum(), nz.min(), nz.max()))
cols = (A>0).any(axis=0)
nzc = np.nonzero(cols)[0]
print("有内容的列: %d   范围 %d..%d" % (cols.sum(), nzc.min(), nzc.max()))
print()
# 每行的非零像素数，找出行带（glyph rows）
cnt = (A>0).sum(axis=1)
print("=== 行分布（前 60 行 + 间隔）===")
bands=[]; inb=False; st=0
for y in range(2048):
    if cnt[y]>0 and not inb: inb=True; st=y
    elif cnt[y]==0 and inb: inb=False; bands.append((st,y-1))
if inb: bands.append((st,2047))
print("  连续非零行带 %d 个" % len(bands))
for b0,b1 in bands[:40]:
    print("    y %4d..%4d  (高 %d)" % (b0,b1,b1-b0+1))
