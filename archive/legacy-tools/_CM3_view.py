import numpy as np
from PIL import Image

RAW = r"F:\sr2-cn\_fontdump\fnt_chinese.tex"
a = np.fromfile(RAW, dtype=np.uint8).reshape(2048, 2048)
im = Image.fromarray(a, "L")
OUT = r"F:\sr2-cn\_crop"

im.resize((1024, 1024), Image.NEAREST).save(OUT + r"\ov_all.png")
im.crop((0, 0, 512, 256)).resize((1024, 512), Image.NEAREST).save(OUT + r"\ov_tl.png")
im.crop((0, 0, 256, 1024)).resize((512, 2048), Image.NEAREST).save(OUT + r"\ov_lft.png")

# 打印列 ink 概况
ink = (a > 110)
cs = ink.sum(axis=0)
print("colsum 0..80:", list(cs[0:80]))
rs = ink.sum(axis=1)
print("rowsum 0..100:", list(rs[0:100]))
print("总墨点:", int(ink.sum()))
print("非零列数:", int((cs > 0).sum()), " 非零行数:", int((rs > 0).sum()))
print("最大列:", int(cs.max()), "最大行:", int(rs.max()))
