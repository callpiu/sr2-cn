# -*- coding: utf-8 -*-
# 对比 patch.vpp_pc 与 textures.vpp_pc 里的 fnt_chinese 图集
import os, sys, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
from PIL import Image, ImageDraw
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def grab(path, nm):
    v = Vpp(path)
    e = v.find(nm, None)
    if e is None:
        e = v.find(nm, "g_peg_pc")
    if e is None:
        print("  not found", nm, "in", path); return None
    d = v.read(e)
    print("  %-24s %s size=%d" % (nm, os.path.basename(path), len(d)))
    return d

A = grab(os.path.join(G, "patch.vpp_pc"), "fnt_chinese")
B = grab(os.path.join(G, "textures.vpp_pc"), "fnt_chinese")
for tag, d in (("patch", A), ("textures", B)):
    if d is None: continue
    import hashlib
    print("  %-9s md5=%s" % (tag, hashlib.md5(d).hexdigest()))

CELLS = [33, 336, 354, 362, 371, 391, 410, 422, 967, 1035, 1190, 1784, 1836, 2268, 2296, 2342, 2656, 2667]
COLS, STEP, SC = 65, 31, 4
CW = 31*SC
sheet = Image.new("RGB", (6*(CW+8), 3*(CW+24)+24), (30,30,30))
d = ImageDraw.Draw(sheet)
for col, (tag, data) in enumerate((("patch", A), ("textures", B))):
    if data is None: continue
    rgb, al = dxt3_decode(data, 2048, 2048)
    img = Image.frombytes("RGB", (2048, 2048), rgb)
    d.text((6, col*(3*(CW+24))+2), "ATLAS=%s" % tag, fill=(120,255,120))
    for n, k in enumerate(CELLS):
        cx = 1+STEP*(k % COLS); cy = 1+STEP*(k//COLS)
        c = img.crop((cx, cy, cx+31, cy+31)).resize((CW, CW), Image.NEAREST)
        px = (n % 6)*(CW+8); py = col*(3*(CW+24)) + 20 + (n//6)*(CW+24)
        sheet.paste(c, (px, py))
        d.text((px+2, py+CW+4), "idx=%d" % k, fill=(255,220,80))
sheet.save(r"F:\sr2-cn\_HQ_cmp.png")
print("saved _HQ_cmp.png")
