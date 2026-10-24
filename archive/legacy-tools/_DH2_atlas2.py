import sys, os
import numpy as np
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode

def stat(tag, p, name, ext):
    v=Vpp(p); e=v.find(name,ext)
    if e is None: print("%-26s MISS"%tag); return
    b=v.read(e); rgb,a=dxt3_decode(b,2048,2048)
    nz=a>0
    mx=rgb.max(axis=2); mn=rgb.min(axis=2)
    grey=(mx-mn)<=2
    d=np.abs(a.astype(int)-mx.astype(int))
    print("%-26s 非透明=%7d 灰度比例=%.3f |a-max(rgb)|中位=%3d >8占比=%.3f  RGB均值=%.1f" % (
        tag, int(nz.sum()), float((nz&grey).sum())/max(1,int(nz.sum())),
        int(np.median(d[nz])) if nz.any() else -1,
        float((nz&(d>8)).sum())/max(1,int(nz.sum())),
        float(mx[nz].mean()) if nz.any() else -1))

stat("官方图集(textures.orig)", r"F:/sr2-cn/vpp_backup/textures.vpp_pc.orig","fnt_chinese",None)
stat("官方图集(patch.orig)",      r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig","fnt_chinese","g_peg_pc")
stat("当前游戏图集(patch)",       r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc","fnt_chinese","g_peg_pc")
stat("当前游戏图集(textures)",    r"G:/SteamLibrary/steamapps/common/Saints Row 2/textures.vpp_pc","fnt_chinese",None)
