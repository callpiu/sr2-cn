import numpy as np
from PIL import Image

# SUB1 starts ~x=784, glyph pitch ~ (1284-784)/11 = 45.5? no -> use detected segment starts
# From _FK8: SUB1 band x0=770 ; segments widths sum -> recompute starts here.
def seg_starts(path, y0, y1, x0, x1):
    im = Image.open(path).convert("RGB")
    a = np.array(im).astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    mask = ((r > 185) & (g > 185) & (b > 185)) | ((g > 140) & (g > r + 45) & (g > b + 45))
    m = mask[y0:y1, x0:x1]
    prof = m.sum(axis=0)
    runs = []; inrun = False; gap = 0
    for x in range(m.shape[1]):
        if prof[x] > 0:
            if not inrun: inrun = True; s = x
            gap = 0
        else:
            if inrun:
                gap += 1
                if gap >= 3: runs.append((s + x0, x - gap + 1 + x0)); inrun = False
    if inrun: runs.append((s + x0, m.shape[1] + x0))
    return im, runs

im1, r1 = seg_starts(r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-613Z-e066f6e6.jpg", 690, 762, 770, 1300)
im2, r2 = seg_starts(r"C:\Users\ezplayer\.workbuddy-ai\clipboard-images\clipboard-2026-10-15T16-54-27-615Z-ef572c30.jpg", 693, 733, 560, 1350)
print("sub1 runs:", r1)
print("sub2 runs:", r2)

def grab(im, x0, x1, y0, y1, k=8):
    c = im.crop((x0-3, y0-4, x1+3, y1+4))
    return c.resize((c.width*k, c.height*k), Image.LANCZOS)

# string1: 11 glyphs but run4 is merged(位雄).  take run index 4 and 5 and 6
tiles = []
for i, (s, e) in enumerate(r1):
    tiles.append(grab(im1, s, e, 690, 762, 6))
W = max(t.width for t in tiles); H = max(t.height for t in tiles)
sheet = Image.new("RGB", (W*len(tiles)+10*len(tiles), H), (30, 30, 30))
x = 0
for t in tiles:
    sheet.paste(t, (x, 0)); x += t.width + 10
sheet.save(r"F:\sr2-cn\_FK9_sub1_tiles.png")
print("sub1 tiles", sheet.size, [ (e-s) for s,e in r1])

tiles2 = []
for i, (s, e) in enumerate(r2):
    tiles2.append(grab(im2, s, e, 693, 733, 6))
W2 = max(t.width for t in tiles2); H2 = max(t.height for t in tiles2)
sheet2 = Image.new("RGB", (W2*len(tiles2)+10*len(tiles2), H2), (30, 30, 30))
x = 0
for t in tiles2:
    sheet2.paste(t, (x, 0)); x += t.width + 10
sheet2.save(r"F:\sr2-cn\_FK9_sub2_tiles.png")
print("sub2 tiles", sheet2.size, [ (e-s) for s,e in r2])
