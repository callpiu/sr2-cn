import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
FONT = r"C:\Windows\Fonts\msyhbd.ttc"
STRIP_H, BASE = 100, 70
for size in (17, 18, 19):
    ft = ImageFont.truetype(FONT, size)
    slot = int(ft.getlength("W")) + 6
    img = Image.new("L", (slot*95, STRIP_H), 0)
    dr = ImageDraw.Draw(img)
    for k, cp in enumerate(range(0x20, 0x7F)):
        dr.text((k*slot + slot//2, BASE), chr(cp), fill=255, font=ft, anchor="ms")
    S = np.asarray(img)
    print("=== 字号 %d  槽宽 %d ===" % (size, slot))
    for ch in "AHWgpy_-,.0":
        k = ord(ch)-0x20
        sub = S[:, k*slot:(k+1)*slot]
        ys = np.nonzero((sub>30).any(axis=1))[0]
        if len(ys):
            print("   %-3r 行 %d..%d  (基线 %d, 高度 %d)" % (ch, ys.min(), ys.max(), BASE, ys.max()-ys.min()+1))
        else:
            print("   %-3r 无墨迹" % ch)
    print()
