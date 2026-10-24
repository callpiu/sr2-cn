import sys, os, struct
import numpy as np
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
W = r"F:\sr2-cn"
v = Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc"))
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
N = struct.unpack_from("<i",vf3,0x08)[0]
U0 = 0xD0+N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
CPS=[int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]

# 只看单个格内 [U, U+31)，避免抓到隔壁字
print("=== 单格内 (U..U+31) 的墨迹范围，前 12 个 ASCII ===")
for i in range(12):
    u=U[i]
    seg = al[1:29, u:u+31]>32
    c=np.nonzero(seg.any(axis=0))[0]
    print("  %-3r U=%-5d 墨迹列 %s  宽 %d" % (chr(CPS[i]), u,
          (int(c.min()),int(c.max())) if len(c) else None,
          int(c.max()-c.min()+1) if len(c) else 0))
print()
# 全 ASCII 的墨迹宽度（单格内）
ws=[]
for i in range(1,95):
    u=U[i]
    seg=al[1:29, u:u+31]>32
    c=np.nonzero(seg.any(axis=0))[0]
    if len(c): ws.append((int(c.min()),int(c.max())))
print("ASCII 单格内墨迹: first 中位数 %d, last 中位数 %d -> 宽中位数 %d" % (
    int(np.median([a for a,b in ws])), int(np.median([b for a,b in ws])),
    int(np.median([b-a+1 for a,b in ws]))))
print("  first 分布: %s" % dict(__import__("collections").Counter([a for a,b in ws]).most_common(6)))
print("  last  分布: %s" % dict(__import__("collections").Counter([b for a,b in ws]).most_common(6)))
print()
# CJK 同样
ws2=[]
for i in range(95, min(N,600)):
    u=U[i]
    if u<0 or u+31>2048: continue
    seg=al[1:29, u:u+31]>32
    c=np.nonzero(seg.any(axis=0))[0]
    if len(c): ws2.append((int(c.min()),int(c.max())))
if ws2:
    print("CJK 单格内墨迹: first 中位数 %d, last 中位数 %d -> 宽中位数 %d" % (
        int(np.median([a for a,b in ws2])), int(np.median([b for a,b in ws2])),
        int(np.median([b-a+1 for a,b in ws2]))))
