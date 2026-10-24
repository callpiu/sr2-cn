import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
W = r"F:\sr2-cn"
v = Vpp(os.path.join(W,"_juice_fix","patch.vpp_pc"))
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N = struct.unpack_from("<i",vf3,0x08)[0]
U0 = 0xD0+N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
WID=[struct.unpack_from("<h",vf3,0xD0+i*16)[0] for i in range(N)]

# 用 31px 网格找到每个 ASCII 字形的真实格位
print("=== 按 31px 网格扫描，看每个格的实际内容 ===")
found = {}
for r in range(0, 4):
    for c in range(66):
        x = 1 + 31*c; y = 1 + 31*r
        if x+20 > 2048 or y+28 > 2048: continue
        m = al[y+4:y+26, x:x+20] > 32
        if m.sum() > 40:
            cols = np.nonzero(m.any(axis=0))[0]
            if len(cols):
                found[(r,c)] = (x, y, int(m.sum()), int(cols.min()), int(cols.max()))
print("  网格行0 有墨迹的格: %d 个" % sum(1 for k in found if k[0]==0))
print("  网格行1 有墨迹的格: %d 个" % sum(1 for k in found if k[0]==1))
print()
print("=== 用 vf3 的 (U,V) 检查：字形在记录的起点是否真的在那里 ===")
print("%-5s %-5s %-14s %-7s %-16s %s" % ("字符","索引","(U,V)","width","框内墨量","判定"))
bad=[]
for cp in list(range(0x20,0x7F)):
    if cp not in [c for c in CPS[:200]]: pass
    i = CPS.index(cp) if cp in CPS else None
    if i is None: continue
    x,y = U[i], V[i]
    m = al[y:y+28, x:x+WID[i]] > 32
    ink = int(m.sum())
    ok = ink > 30 or cp == 0x20
    if not ok: bad.append(chr(cp))
    if cp < 0x30 or chr(cp) in "nso":
        print("%-5r %-5d (%4d,%3d)     %-7d %-16d %s" % (chr(cp), i, x, y, WID[i], ink, "OK" if ok else "★ 缺墨迹"))
print()
print("墨迹不足的字符 (%d 个): %s" % (len(bad), "".join(bad)))
