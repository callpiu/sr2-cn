import numpy as np
RAW = r"F:\sr2-cn\_fontdump\fnt_chinese.tex"
a = np.fromfile(RAW, dtype=np.uint8).reshape(2048, 2048)

print("列配对 a[:,0::2]==a[:,1::2] 比例: %.4f" % (a[:, 0::2] == a[:, 1::2]).mean())
print("行配对 a[0::2,:]==a[1::2,:] 比例: %.4f" % (a[0::2, :] == a[1::2, :]).mean())
b = a[:, 0::2]
print("取偶列后 1024x2048: 行配对比例 %.4f" % (b[0::2, :] == b[1::2, :]).mean())
print("取偶列后 列配对(再隔2) %.4f" % (b[:, 0::2] == b[:, 1::2]).mean())

# 16bpp 解成 uint16
u16 = np.frombuffer(open(RAW, "rb").read(), dtype="<u2")
print("\n16bpp LE 解出 %d 像素 = %dx%d 或 %dx%d" % (len(u16), 2048, 1024, 1024, 2048))
g16 = u16.reshape(2048, 1024).astype(np.float64) / 65535.0
print("16bpp(2048x1024) min/max/mean: %.4f %.4f %.4f" % (g16.min(), g16.max(), g16.mean()))
print("16bpp 高位字节全 0 比例: %.4f" % (u16 >> 8 == 0).mean())
print("16bpp 是否像 8bit 扩展(高=低): %.4f" % ((u16 >> 8) == (u16 & 0xFF)).mean())
print("16bpp 是否像 8bit 扩展(高=0): %.4f" % ((u16 >> 8) == 0).mean())
print("16bpp 是否像 8bit 扩展(高=255): %.4f" % ((u16 >> 8) == 255).mean())
