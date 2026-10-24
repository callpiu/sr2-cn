"""FU1: decode the INSTALLED atlas and crop the cells that the two broken
subtitles actually reference, so we can see WHICH glyph is really stored there.

String 1 correct : 你的弟兄们需要你的保护
  codes-32 (glyph slots the engine asks for): [371,1836,1035,422,332,2667,2296,371,1836,391,1190]
String 1 on screen: 任璨偶巧位雄衡任璨伪该
  M.index() of those chars               : [336,1784,410,967,362,2656,2268,336,1784,354,2342]
"""
import sys, os
sys.path.insert(0, r"F:\sr2-cn")
import numpy as np
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:\sr2-cn\_FU1_atlas.png"

SLOTS = [371, 1836, 1035, 422, 332, 2667, 2296, 371, 1836, 391, 1190]
GSLOT = [336, 1784, 410, 967, 362, 2656, 2268, 336, 1784, 354, 2342]

# --- load installed atlas (the one the game really uses) ---
def atlas_from(path, name, ext):
    v = Vpp(path)
    e = v.find(name, ext) if ext else v.find(name)
    print("  found", name, ext, "->", e["name"], e["ext"], "size", e["size"])
    return v.read(e)

print("installed textures.vpp_pc / fnt_chinese (no ext):")
raw = atlas_from(os.path.join(G, "textures.vpp_pc"), "fnt_chinese", None)
print("  md5-ish len:", len(raw))

rgb, alpha = dxt3_decode(raw, 2048, 2048)
print("  decoded", rgb.shape, "alpha max", int(alpha.max()))

PITCH = 31
def cell(idx, cols, off, step):
    col = idx % cols
    row = idx // cols
    x = off + step * col
    y = off + step * row
    return alpha[y:y+PITCH, x:x+PITCH]

def sheet(indices, cols, off, step, label):
    tiles = []
    for i in indices:
        t = cell(i, cols, off, step)
        tiles.append(t)
    return np.concatenate(tiles, axis=1)

# try the two candidate layouts
for cols, off, step, tag in [(65, 1, 31, "65col"), (66, 1, 31, "66col"), (66, 2, 31, "66col_off2")]:
    a = sheet(SLOTS, cols, off, step, "expected")
    b = sheet(GSLOT, cols, off, step, "garbled")
    sep = np.full((PITCH, 12), 255, np.uint8)
    row = np.concatenate([a, sep, b], axis=1)
    print("%-10s width=%d" % (tag, row.shape[1]))

# save the 65col version, upscaled 6x, as a viewable png
def up(a, k=6):
    return np.kron(a, np.ones((k, k), np.uint8))

a = sheet(SLOTS, 65, 1, 31, "expected")
b = sheet(GSLOT, 65, 1, 31, "garbled")
sep = np.full((PITCH, 4), 255, np.uint8)
row = np.concatenate([a, sep, b], axis=1)
img = up(row, 6)
try:
    from PIL import Image
    Image.fromarray(img, "L").save(OUT)
    print("saved", OUT, img.shape)
except Exception as ex:
    print("PIL fail", ex)
    np.save(r"F:\sr2-cn\_FU1_atlas.npy", row)
