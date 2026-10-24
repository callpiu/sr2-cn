import numpy as np
from PIL import Image

a = np.fromfile(r"F:\sr2-cn\_fontdump\game_patch.tex", dtype=np.uint8).reshape(2048, 2048)
im = Image.fromarray(a, "L")
SC = 7

def cell(i):
    c = i % 65; r = i // 65
    x = 1 + 31 * c; y = 1 + 31 * r
    return im.crop((x, y, x + 31, y + 31)).resize((31 * SC, 31 * SC), Image.NEAREST)

correct = [371, 1836, 1035, 422, 332, 2667, 2296, 391, 1190]   # 你的弟兄们需要保护
rendered = [336, 1784, 410, 967, 362, 2656, 2268, 354, 2342]  # 任璨偶巧位雄衡伪该

W = 31 * SC
sheet = Image.new("L", (W * 9, W * 2 + 20), 0)
for k, i in enumerate(correct):
    sheet.paste(cell(i), (k * W, 0))
for k, i in enumerate(rendered):
    sheet.paste(cell(i), (k * W, W + 20))
sheet.save(r"F:\sr2-cn\_crop\sheet_idx.png")
print("saved", sheet.size, "上排=正确下标(你的弟兄们需要保护) 下排=乱码字下标")
for k, (ci, ri) in enumerate(zip(correct, rendered)):
    print("  #%d 正确idx=%d (r=%d,c=%d)  乱码idx=%d (r=%d,c=%d)" % (k, ci, ci // 65, ci % 65, ri, ri // 65, ri % 65))
