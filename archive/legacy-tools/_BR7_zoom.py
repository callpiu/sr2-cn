# -*- coding: utf-8 -*-
from PIL import Image
import os
OUT = r"F:\sr2-cn\_crop"
os.makedirs(OUT, exist_ok=True)
P = r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T08-17-55-901Z-fad3050f.jpg"
im = Image.open(P)
# 字幕带
band = im.crop((560, 690, 1470, 745))
w, h = band.size
band = band.resize((w * 6, h * 6), Image.LANCZOS)
band.save(os.path.join(OUT, "fad_band.png"))
print("band", band.size)
# 左右两半
hw = band.size[0] // 2
band.crop((0, 0, hw + 60, band.size[1])).save(os.path.join(OUT, "fad_L.png"))
band.crop((hw - 60, 0, band.size[0], band.size[1])).save(os.path.join(OUT, "fad_R.png"))
print("ok")
