import numpy as np
from PIL import Image

RAW = r"F:\sr2-cn\_fontdump\fnt_chinese.tex"
a = np.fromfile(RAW, dtype=np.uint8).reshape(2048, 2048)
im = Image.fromarray(a, "L")
O = r"F:\sr2-cn\_crop"
im.crop((0, 0, 64, 64)).resize((512, 512), Image.NEAREST).save(O + r"\z_00.png")
im.crop((0, 0, 256, 32)).resize((1536, 192), Image.NEAREST).save(O + r"\z_row0.png")
im.crop((0, 8, 512, 40)).resize((1536, 96), Image.NEAREST).save(O + r"\z_rowA.png")
im.crop((496, 56, 1008, 96)).resize((1536, 120), Image.NEAREST).save(O + r"\z_rowB.png")
print("ok")
