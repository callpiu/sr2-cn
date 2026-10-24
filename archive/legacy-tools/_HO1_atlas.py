# -*- coding: utf-8 -*-
# 解出 fnt_chinese 图集，裁出关键格子，做成带索引标注的对照图
import os, sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
from PIL import Image, ImageDraw

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
T = os.path.join(G, "textures.vpp_pc")
v = Vpp(T)
e = v.find("fnt_chinese", None)
print("entry:", e)
data = v.read(e)
print("bytes:", len(data))

W = H = 2048
rgb, alpha = dxt3_decode(data, W, H)
print("decoded", len(rgb), len(alpha))
img = Image.frombytes("RGB", (W, H), rgb)
img.save(r"F:\sr2-cn\_HO_atlas_full.png")
print("saved full")

# 用 65 列 / 31 步距 裁格子
CELLS = [33, 336, 354, 362, 371, 391, 410, 422, 967, 1035, 1190, 1784, 1836, 2268, 2296, 2342, 2656, 2667]
COLS, STEP = 65, 31
SC = 4
CW = 31 * SC
SHEET_COLS = 6
rows = (len(CELLS) + SHEET_COLS - 1) // SHEET_COLS
sheet = Image.new("RGB", (SHEET_COLS*(CW+8), rows*(CW+24)), (30,30,30))
d = ImageDraw.Draw(sheet)
for n, k in enumerate(CELLS):
    cx = 1 + STEP * (k % COLS); cy = 1 + STEP * (k // COLS)
    c = img.crop((cx, cy, cx+31, cy+31)).resize((CW, CW), Image.NEAREST)
    px = (n % SHEET_COLS) * (CW+8); py = (n // SHEET_COLS) * (CW+24)
    sheet.paste(c, (px, py))
    d.text((px+2, py+CW+4), "idx=%d" % k, fill=(255,220,80))
sheet.save(r"F:\sr2-cn\_HO_cells.png")
print("saved cells", CELLS)
