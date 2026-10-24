# -*- coding: utf-8 -*-
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp, dxt3_decode
from PIL import Image
import numpy as np
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

# jap 图集
v = Vpp(os.path.join(G, "textures.vpp_pc"))
tex = v.read(v.find("jap", ""))
rgb, alpha = dxt3_decode(tex, 2048, 1024)
print("jap 图集解码:", rgb.shape, alpha.shape)

# jap vf3
v2 = Vpp(os.path.join(G, "patch.vpp_pc"))
vf3 = v2.read(v2.find("jap", "vf3_pc"))
N = struct.unpack_from("<I", vf3, 8)[0]
uoff = 0xD0 + N*16
U = list(struct.unpack_from("<%di" % N, vf3, uoff))
V = list(struct.unpack_from("<%di" % (N-5), vf3, uoff + N*4))

canvas = Image.new("RGB", (31*12, 31*4), (20, 20, 30))
px = canvas.load()
cells = [(371,"你"), (1836,"的"), (1035,"弟"), (422,"兄"), (332,"们"),
         (2667,"需"), (2296,"要"), (391,"保"), (1190,"护")]
out = Image.new("L", (31*len(cells), 40), 0)
for i, (idx, ch) in enumerate(cells):
    if idx >= N:
        print("idx %d 越界" % idx); continue
    x, y = U[idx], V[idx]
    w, h, a, b = struct.unpack_from("<HHHH", vf3, 0xD0 + idx*16)
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(2048, x0+32), min(1024, y0+32)
    sub = alpha[y0:y1, x0:x1]
    img = Image.fromarray(sub)
    out.paste(img.resize((32, 32)), (i*31, 4))
    print("  idx=%-5d %s  U=%d V=%d  FontChar w=%d h=%d" % (idx, ch, x, y, w, h))
out = out.resize((out.width*4, out.height*4), Image.NEAREST)
out.save(r"F:/sr2-cn/_JAP_cells.png")
print("已保存 _JAP_cells.png  (顺序: 你的弟兄们需要保护)")
