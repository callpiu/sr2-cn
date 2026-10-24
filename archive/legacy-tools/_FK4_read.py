import numpy as np
from PIL import Image

jobs = [
    (r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg",
     (784, 693, 1284, 757), "s1"),
    (r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-615Z-ef572c30.jpg",
     (382, 655, 1336, 790), "s2"),
]
for p, box, tag in jobs:
    im = Image.open(p).convert("RGB")
    c = im.crop(box)
    n = 3
    step = c.width // n + 1
    for i in range(n):
        seg = c.crop((i*step, 0, min(c.width, (i+1)*step+12), c.height))
        seg = seg.resize((seg.width*5, seg.height*5), Image.LANCZOS)
        out = r"F:\sr2-cn\_FK4_%s_%d.png" % (tag, i)
        seg.save(out)
        print(out, seg.size)
