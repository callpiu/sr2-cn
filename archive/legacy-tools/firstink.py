import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
W = r"F:\sr2-cn"
v = Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc"))
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
N = struct.unpack_from("<i",vf3,0x08)[0]
U0 = 0xD0+N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
idx = {}
for i,cp in enumerate(CPS):
    if 0x20<=cp<=0x7E: idx.setdefault(cp,i)

# 「第一列」规则：真正的字形在 [U+step, U+2*step) 内？
def ink_cols(i, win=64):
    u = U[i]
    seg = al[1:29, u:min(u+win,2048)] > 32
    c = np.nonzero(seg.any(axis=0))[0]
    return (int(c.min()), int(c.max())) if len(c) else None

print("=== 每个 ASCII 字：U 起点后第几列开始有墨迹 ===")
rows=[]
for i in range(95):
    r = ink_cols(i, 70)
    rows.append((i, chr(CPS[i]), U[i], r))
for i,ch,u,r in rows[:20]:
    print("  %-3r U=%-5d 墨迹列 %s" % (ch, u, r))
print("  ...")
print()
# 统计「第一个有墨迹的列」的分布（只在中心±20范围内找，避免抓到隔壁字）
firsts=[]
for i in range(1,95):
    u=U[i]
    seg = al[1:29, u:min(u+40,2048)]>32
    c=np.nonzero(seg.any(axis=0))[0]
    if len(c): firsts.append(int(c.min()))
import collections
print("第一个墨迹列的分布: %s" % dict(collections.Counter(firsts).most_common(12)))
print("中位数: %d" % int(np.median(firsts)))
print()
# 同理看最后墨迹列相对 U 的偏移
lasts=[]
for i in range(1,95):
    u=U[i]
    seg = al[1:29, u:min(u+40,2048)]>32
    c=np.nonzero(seg.any(axis=0))[0]
    if len(c): lasts.append(int(c.max()))
print("最后一个墨迹列分布: %s" % dict(collections.Counter(lasts).most_common(8)))
