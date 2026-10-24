import numpy as np
RAW = r"F:\sr2-cn\_fontdump\fnt_chinese.tex"
a = np.fromfile(RAW, dtype=np.uint8).reshape(2048, 2048)
print("dtype", a.dtype, "min", a.min(), "max", a.max(), "mean", round(float(a.mean()),2))
print("唯一值个数:", len(np.unique(a)))
print("前 20 个唯一值:", np.unique(a)[:20])
vals, cnts = np.unique(a, return_counts=True)
top = sorted(zip(cnts, vals), reverse=True)[:12]
print("最常见值:", [(int(v), int(c)) for c, v in top])
print()
print("=== 原始字节 y=8..20, x=0..24 ===")
hdr = "     " + "".join("%4d" % x for x in range(0, 24, 4))
print(hdr)
for y in range(8, 21):
    print("%4d %s" % (y, "".join("%4d" % a[y, x] for x in range(0, 24, 4))))
print()
# 每行非零计数
nz = (a > 0).sum(axis=1)
print("每行非零像素数 y=0..48:", list(nz[0:48]))
nzc = (a > 0).sum(axis=0)
print("每列非零像素数 x=0..48:", list(nzc[0:48]))
