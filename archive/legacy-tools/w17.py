import sys, os, struct
import numpy as np
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0+N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
WID=[struct.unpack_from("<h",vf3,0xD0+i*16)[0] for i in range(N)]
print("=== width != 30 的记录（除了我改过的 ASCII 0..94）===")
for i in range(95, N):
    if WID[i] != 30:
        print("  idx %-5d 码点 %-6d %-3s width=%d" % (i, CPS[i], chr(CPS[i]) if CPS[i]>0x100 else "?", WID[i]))
        if i > 200: break
print()
print("=== 伽 的记录 ===")
i = CPS.index(ord("伽"))
rec = struct.unpack_from("<8h", vf3, 0xD0+i*16)
print("  伽 idx=%d U=%d V=%d 记录=%s" % (i, U[i], V[i], rec))
seg = al[V[i]:V[i]+28, U[i]:U[i]+40] > 32
c = np.nonzero(seg.any(axis=0))[0]
lo, hi = (int(c.min()), int(c.max())) if len(c) else (None, None)
print("  墨迹列 %s..%s" % (lo, hi))
iA = CPS.index(ord("A"))
segA = al[V[iA]:V[iA]+28, U[iA]:U[iA]+40] > 32
cA = np.nonzero(segA.any(axis=0))[0]
print("  A   idx=%d U=%d V=%d width=%d 墨迹列 %d..%d" % (iA, U[iA], V[iA], WID[iA], int(cA.min()), int(cA.max())))
