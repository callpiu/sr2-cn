import os
from PIL import Image

imgs = [
    (r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg", "img1"),
    (r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-615Z-ef572c30.jpg", "img2"),
]
for p, tag in imgs:
    im = Image.open(p).convert("RGB")
    W, H = im.size
    print(tag, "size", W, H)
    box = (int(W*0.20), int(H*0.58), int(W*0.85), int(H*0.84))
    c = im.crop(box)
    c = c.resize((c.width*3, c.height*3), Image.LANCZOS)
    out = r"F:\sr2-cn\_ES_%s_sub.png" % tag
    c.save(out)
    print("   ->", out, c.size)
