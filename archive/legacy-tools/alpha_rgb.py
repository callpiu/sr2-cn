import sys, os, struct
import numpy as np
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
rgb, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0+N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
WID=[struct.unpack_from("<h",vf3,0xD0+i*16)[0] for i in range(N)]
print("%-6s %-6s %-16s %-10s %-10s %s" % ("字符","索引","(U,V,width)","alpha墨量","RGB墨量","RGB采样值"))
for ch in "A伽马阴影过":
    if ord(ch) not in CPS: print("  %s 不在表" % ch); continue
    i = CPS.index(ord(ch)); x,y,w = U[i], V[i], WID[i]
    a = al[y:y+28, x:x+max(w,17)]
    r = rgb[y:y+28, x:x+max(w,17)]
    ai = int((a>32).sum()); ri = int((r>32).sum())
    print("%-6s %-6d (%4d,%3d,%2d)   %-10d %-10d %s" % (ch, i, x, y, w, ai, ri, r.reshape(-1,3).mean(axis=0).round(0)))
print()
# 整幅图 alpha vs rgb 的非零率
print("整幅图: alpha>32 占比 %.1f%%, RGB均值>32 占比 %.1f%%" % (
    100*(al>32).mean(), 100*(rgb.mean(axis=2)>32).mean()))
