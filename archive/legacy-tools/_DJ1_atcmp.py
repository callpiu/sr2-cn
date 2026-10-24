import sys, os, hashlib
import numpy as np
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
def loadat(p,name,ext):
    v=Vpp(p); e=v.find(name,ext); return v.read(e)
A = loadat(r"F:/sr2-cn/vpp_backup/textures.vpp_pc.orig","fnt_chinese",None)   # 62a57046
B = loadat(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig","fnt_chinese","g_peg_pc")# a8c33f12
C = loadat(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc","fnt_chinese","g_peg_pc") # 340340761
for t,b in (("官方textures",A),("官方patch",B),("我的部署",C)):
    print("%-12s %8d md5=%s" % (t, len(b), hashlib.md5(b).hexdigest()[:12]))
def cmp(x,y,nx,ny):
    a=np.frombuffer(x,np.uint8); b=np.frombuffer(y,np.uint8)
    diff=(a!=b)
    idx=np.nonzero(diff)[0]
    print("  %-22s 不同字节=%8d (%.1f%%)  首差=%s  末差=%s" % (nx+" vs "+ny, diff.sum(), 100*diff.mean(),
          idx[0] if len(idx) else None, idx[-1] if len(idx) else None))
    if len(idx):
        # 首个不同块的行列
        p=int(idx[0]); print("     首个差在字节 %d -> 像素行=%d 列=%d (DXT3块 row=%d col=%d)" % (p, (p//2048), (p%2048), (p//16)//128, (p//16)%128))
print()
cmp(B,C,"官方patch","我的部署")
cmp(A,B,"官方textures","官方patch")
cmp(A,C,"官方textures","我的部署")
# 我的部署 是不是官方patch 的某个偏移版本
b=np.frombuffer(B,np.uint8); c=np.frombuffer(C,np.uint8)
best=None
for sh in range(0, 4096):
    d=(b[sh:sh+len(c)] != c).sum() if sh else (b!=c).sum()
    if best is None or d<best[1]: best=(sh,d)
print("\n最小差异偏移扫描: 偏移=%d 时不同字节=%d" % best)
