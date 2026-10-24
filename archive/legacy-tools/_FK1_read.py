import numpy as np
from PIL import Image

for p, tag in [
    (r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg", "sub1"),
    (r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-615Z-ef572c30.jpg", "sub2"),
]:
    im = Image.open(p).convert("RGB")
    a = np.array(im).astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    bright = (r > 205) & (g > 205) & (b > 205)
    sub = np.zeros_like(bright)
    sub[560:780, 250:1750] = bright[560:780, 250:1750]
    ys, xs = np.where(sub)
    print(tag, "bright px", len(ys))
    if len(ys):
        y0, y1 = max(0, ys.min()-8), ys.max()+9
        x0, x1 = max(0, xs.min()-8), xs.max()+9
        print("   bbox y=%d..%d x=%d..%d  (h=%d w=%d)" % (y0, y1, x0, x1, y1-y0, x1-x0))
        c = im.crop((x0, y0, x1, y1))
        c = c.resize((c.width*4, c.height*4), Image.LANCZOS)
        out = r"F:\sr2-cn\_FK_%s.png" % tag
        c.save(out)
        print("   ->", out, c.size)
