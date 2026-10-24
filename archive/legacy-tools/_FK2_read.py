import numpy as np
from PIL import Image

for p, tag in [
    (r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg", "sub1"),
    (r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-615Z-ef572c30.jpg", "sub2"),
]:
    im = Image.open(p).convert("RGB")
    W, H = im.size
    print(tag, "size", W, H)
    a = np.array(im).astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    bright = (r > 200) & (g > 200) & (b > 200)
    # subtitle band = middle-lower, centre third
    band = np.zeros_like(bright)
    band[int(H*0.60):int(H*0.80), int(W*0.20):int(W*0.85)] = bright[int(H*0.60):int(H*0.80), int(W*0.20):int(W*0.85)]
    ys, xs = np.where(band)
    print("   bright px", len(ys))
    if len(ys):
        y0, y1 = max(0, ys.min()-6), ys.max()+7
        x0, x1 = max(0, xs.min()-6), xs.max()+7
        print("   bbox y=%d..%d x=%d..%d (h=%d w=%d)" % (y0, y1, x0, x1, y1-y0, x1-x0))
        c = im.crop((x0, y0, x1, y1))
        k = max(1, 1400 // max(1, c.width))
        c = c.resize((c.width*k, c.height*k), Image.LANCZOS)
        out = r"F:\sr2-cn\_FK2_%s.png" % tag
        c.save(out)
        print("   ->", out, c.size, "zoom", k)
