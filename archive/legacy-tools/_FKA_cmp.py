import numpy as np
from PIL import Image

im1 = Image.open(r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg").convert("RGB")
im2 = Image.open(r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-615Z-ef572c30.jpg").convert("RGB")

crops = [
    ("s1 g6 雄?", im1, (944, 688, 980, 764)),
    ("s1 g7 衡?", im1, (977, 688, 1010, 764)),
    ("s2 g6 校?", im2, (772, 691, 805, 735)),
    ("s2 g7 衡?", im2, (804, 691, 837, 735)),
]
k = 9
tiles = []
for name, im, box in crops:
    c = im.crop(box)
    c = c.resize((c.width*k, c.height*k), Image.LANCZOS)
    tiles.append((name, c))
    print(name, c.size)

W = sum(t.width for _, t in tiles) + 30*len(tiles)
H = max(t.height for _, t in tiles)
sheet = Image.new("RGB", (W, H), (20, 20, 20))
x = 0
for _, t in tiles:
    sheet.paste(t, (x, 0)); x += t.width + 30
sheet.save(r"F:\sr2-cn\_FKA_cmp67.png")
print("saved", sheet.size)
