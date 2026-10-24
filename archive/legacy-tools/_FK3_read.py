import numpy as np
from PIL import Image

p = r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-615Z-ef572c30.jpg"
im = Image.open(p).convert("RGB")
W, H = im.size
a = np.array(im).astype(np.int16)
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
bright = (r > 190) & (g > 190) & (b > 190)
band = np.zeros_like(bright)
y0b, y1b, x0b, x1b = 640, 800, 350, 1400
band[y0b:y1b, x0b:x1b] = bright[y0b:y1b, x0b:x1b]
ys, xs = np.where(band)
print("bright", len(ys), "y", ys.min(), ys.max(), "x", xs.min(), xs.max())

# column profile to find glyph cells
prof = band.sum(axis=0)
runs = []
inrun = False
for x in range(x0b, x1b):
    if prof[x] > 0 and not inrun:
        inrun = True; s = x
    elif prof[x] == 0 and inrun:
        inrun = False; runs.append((s, x))
if inrun: runs.append((s, x1b))
print("runs:", len(runs))
for i, (s, e) in enumerate(runs):
    print("  %2d  x=%4d..%4d  w=%d" % (i, s, e, e - s))

c = im.crop((xs.min()-6, ys.min()-8, xs.max()+7, ys.max()+9))
c = c.resize((c.width*3, c.height*3), Image.LANCZOS)
out = r"F:\sr2-cn\_FK3_sub2.png"
c.save(out)
print("saved", out, c.size)
