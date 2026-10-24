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
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]

# 检查每个 ASCII 字：改 width 到 31 后，区间 [U, U+31] 是否含完整字形且不侵入下一个
print("%-5s %-6s %-14s %-10s %-10s %s" % ("字符","索引","U","改后区间","下一字U","判定"))
alerts=[]
for i in range(95):
    u = U[i]
    nxt = U[i+1] if i+1 < 95 else u+31
    # 区间 [u, u+31) 内的墨迹
    seg = al[1:29, u:u+31] > 32
    ink = int(seg.sum())
    # 是否会侵入下一个（即下一个字的墨迹是否落进本区间）
    nseg = al[1:29, nxt:nxt+31] > 32
    overlap = int((al[1:29, u+31:max(u+31,nxt)]>32).sum()) if nxt > u+31 else 0
    ok = (nxt - u) >= 31
    if not ok: alerts.append((i, chr(CPS[i]), nxt-u))
    if i < 8 or i in (33,36,78,83,89):
        print("%-5r %-6d %-14d [%d,%d)  %-10d %s" % (chr(CPS[i]), i, u, u, u+31, nxt,
              "OK" if ok else "★ 步距仅 %d" % (nxt-u)))
print()
print("步距 < 31 的 ASCII 字 (%d 个): %s" % (len(alerts), alerts[:20]))
print()
# 全表步距统计
steps = [U[i+1]-U[i] for i in range(N-1)]
import collections
print("全表步距分布 (前 10 种):")
for s,c in collections.Counter(steps).most_common(10):
    print("  步距 %-5d : %d 处" % (s,c))
