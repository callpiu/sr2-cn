# -*- coding: utf-8 -*-
"""高清裁剪截图中的字幕/HUD 文字"""
from PIL import Image
import os

S1 = r'C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T14-27-45-539Z-e066f6e6.jpg'
S2 = r'C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-14T08-17-55-901Z-fad3050f.jpg'
OUT = r'F:\sr2-cn\_crop'

def crop(src, name, box, scale=5):
    im = Image.open(src)
    c = im.crop(box)
    c = c.resize((c.width * scale, c.height * scale), Image.LANCZOS)
    p = os.path.join(OUT, name + '.png')
    c.save(p)
    print("saved", p, im.size, box, "->", c.size)

# S1 字幕: 全图 1080x608 左右
crop(S1, 'h_s1_sub', (410, 430, 300, 40), 5)
# S2 字幕
crop(S2, 'h_s2_sub', (330, 385, 400, 40), 5)
# S2 HUD 面板
crop(S2, 'h_s2_hud', (80, 55, 300, 70), 5)
