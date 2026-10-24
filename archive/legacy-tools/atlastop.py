import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
W = r"F:\sr2-cn"
v = Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc"))
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
# 直接按图集原始坐标看顶部 400 行
top = al[0:400, 0:2048]
Image.fromarray(255-top).resize((1024, 200), Image.LANCZOS).save(os.path.join(W,"_juice_fix","atlas_top.png"))
print("写出 atlas_top.png (图集 0..400 行，缩到 1024x200)")
# 找有墨迹的行段
cnt=(al>32).sum(axis=1)
bands=[]; inb=False
for y in range(2048):
    if cnt[y]>0 and not inb: inb=True; st=y
    elif cnt[y]==0 and inb: inb=False; bands.append((st,y-1))
if inb: bands.append((st,2047))
print("有墨迹的连续行段 %d 个，前 20 个:" % len(bands))
for b0,b1 in bands[:20]:
    print("  y %4d..%4d (高 %d)  该段最大行墨量 %d" % (b0,b1,b1-b0+1, max(int(cnt[y]) for y in range(b0,b1+1))))
