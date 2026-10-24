# -*- coding: utf-8 -*-
from PIL import Image
import os
OUT = r"F:\sr2-cn\_crop"
os.makedirs(OUT, exist_ok=True)
jobs = [
    ("e066_sub", r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T14-27-45-539Z-e066f6e6.jpg", (500, 690, 1450, 750)),
    ("fad_sub",  r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T08-17-55-901Z-fad3050f.jpg", (400, 680, 1500, 750)),
    ("fad_hud",  r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T08-17-55-901Z-fad3050f.jpg", (100, 60, 700, 220)),
    ("e066_hud", r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T14-27-45-539Z-e066f6e6.jpg", (100, 60, 700, 220)),
]
for tag, p, box in jobs:
    im = Image.open(p).crop(box)
    w, h = im.size
    im = im.resize((w * 3, h * 3), Image.LANCZOS)
    f = os.path.join(OUT, tag + ".png"); im.save(f)
    print(tag, "->", f, im.size)
