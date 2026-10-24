import numpy as np
from PIL import Image

p = r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-615Z-ef572c30.jpg"
im = Image.open(p).convert("RGB")
c = im.crop((572, 693, 1345, 733))
n = 3
step = c.width // n
for i in range(n):
    seg = c.crop((i*step, 0, min(c.width, (i+1)*step+10), c.height))
    seg = seg.resize((seg.width*5, seg.height*5), Image.LANCZOS)
    out = r"F:\sr2-cn\_FK7_s2_%d.png" % i
    seg.save(out)
    print(out, seg.size)
