import sys, os, hashlib
import numpy as np
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def get_atlas(tag, p, name, ext):
    v=Vpp(p)
    e=v.find(name, ext)
    if e is None: print(tag,"MISS"); return None
    b=v.read(e)
    rgb,a = dxt3_decode(b,2048,2048)
    return b, rgb, a

print("=== 当前游戏图集 (patch.vpp_pc / fnt_chinese / g_peg_pc) ===")
b,rgb,a = get_atlas("cur", os.path.join(G,"patch.vpp_pc"), "fnt_chinese","g_peg_pc")
nz = a>0
print("  非透明像素:", int(nz.sum()))
# RGB 是否随 alpha（灰度镜像）
mx = rgb.max(axis=2); mn = rgb.min(axis=2)
isgrey = (mx-mn) <= 2
print("  非透明像素中 RGB 近似灰度:", int((nz & isgrey).sum()), "/", int(nz.sum()))
sample = np.where(nz)
if len(sample[0]):
    idx=[0, len(sample[0])//4, len(sample[0])//2, -1]
    for k in idx:
        y,x = sample[0][k], sample[1][k]
        print("    (y=%d,x=%d) a=%3d rgb=%s" % (y,x,a[y,x], rgb[y,x].tolist()))
# alpha==max(rgb) 的比例
am = a.astype(int); mm = mx.astype(int)
d = np.abs(am-mm)
print("  |alpha-max(rgb)| 分布: 中位=%d 均值=%.1f  >8 的像素=%d" % (int(np.median(d[nz])) if nz.any() else -1, float(d[nz].mean()) if nz.any() else -1, int((nz & (d>8)).sum())))
print("  全黑(RGB=0)但 alpha>0 的像素:", int((nz & (mx==0)).sum()))
