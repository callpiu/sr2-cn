# -*- coding: utf-8 -*-
from PIL import Image
import os
OUT = r"F:\sr2-cn\_crop"
os.makedirs(OUT, exist_ok=True)
P = r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T08-17-55-901Z-fad3050f.jpg"
im = Image.open(P)
# 字幕首字附近
for tag, box in [("z1", (640, 695, 800, 745)), ("z2", (800, 695, 960, 745)), ("z3", (1200, 695, 1360, 745))]:
    c = im.crop(box)
    w, h = c.size
    c = c.resize((w * 10, h * 10), Image.NEAREST)
    c.save(os.path.join(OUT, tag + ".png"))
    print(tag, c.size)
