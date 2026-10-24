import numpy as np
from PIL import Image

p = r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-615Z-ef572c30.jpg"
im = Image.open(p).convert("RGB")
a = np.array(im).astype(np.int16)
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
bright = (r > 190) & (g > 190) & (b > 190)
sub = bright[:, 380:1340]
rowp = sub.sum(axis=1)
for y in range(600, 820):
    if rowp[y] > 5:
        print(y, rowp[y])
