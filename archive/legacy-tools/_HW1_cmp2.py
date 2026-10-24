# -*- coding: utf-8 -*-
# 对比官方图集 vs 汉化图集：官方 cell k 是否 = 官方 charlist[k]
import os, sys, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
from PIL import Image, ImageDraw
G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
OF = r"F:/sr2-cn/pristine/patch.vpp_pc"

def cl(buf):
    m = re.search(rb'count\s*=\s*(\d+)', buf)
    seg = buf[m.end():] if m else buf
    return [int(x) for x in re.findall(rb'\d+', seg)]

vG = Vpp(os.path.join(G, "patch.vpp_pc")); vO = Vpp(OF)
LC = cl(vG.read(vG.find("charlist_CH","txt")))     # 汉化 2795
LO = cl(vO.read(vO.find("charlist_CH","txt")))     # 官方 2838
dG = vG.read(vG.find("fnt_chinese", None))
dO = vO.read(vO.find("fnt_chinese", None))
print("汉化 atlas", len(dG), " 官方 atlas", len(dO))

CELLS = [33, 336, 354, 362, 371, 391, 410, 422, 967, 1035, 1190, 1784, 1836, 2268, 2296, 2342, 2656, 2667]
COLS, STEP, SC = 65, 31, 4
CW = 31*SC
sheet = Image.new("RGB", (6*(CW+8), 2*(3*(CW+24))+40), (30,30,30))
d = ImageDraw.Draw(sheet)
imgs = {}
for tag, data in (("汉化", dG), ("官方", dO)):
    rgb, al = dxt3_decode(data, 2048, 2048)
    imgs[tag] = Image.frombytes("RGB", (2048,2048), rgb)

for col, (tag, src) in enumerate((("汉化(期望=LC[k])", "汉化"), ("官方(期望=LO[k])", "官方"))):
    img = imgs[src]
    L = LC if src=="汉化" else LO
    d.text((6, col*(3*(CW+24))+2), tag, fill=(120,255,120))
    for n, k in enumerate(CELLS):
        cx = 1+STEP*(k % COLS); cy = 1+STEP*(k//COLS)
        c = img.crop((cx, cy, cx+31, cy+31)).resize((CW,CW), Image.NEAREST)
        px = (n % 6)*(CW+8); py = col*(3*(CW+24)) + 20 + (n//6)*(CW+24)
        sheet.paste(c, (px, py))
        want = chr(L[k]) if k < len(L) else '?'
        d.text((px+2, py+CW+4), "k=%d %s" % (k, want), fill=(255,220,80))
sheet.save(r"F:\sr2-cn\_HW_cmp2.png")
print("saved")

# 官方 charlist 前几项 & k=371
print("官方 LO[336]=%s LO[371]=%s LO[391]=%s" % (chr(LO[336]), chr(LO[371]), chr(LO[391])))
print("汉化 LC[336]=%s LC[371]=%s LC[391]=%s" % (chr(LC[336]), chr(LC[371]), chr(LC[391])))
