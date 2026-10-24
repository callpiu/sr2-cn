import sys, os, struct
import numpy as np
from PIL import Image
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
print("ASCII width (0..5): %s" % WID[:6])
print("CJK   width (95..100): %s" % WID[95:101])
print()
# 伽 的记录
i = CPS.index(ord("伽"))
print("伽 idx=%d  U=%d V=%d width=%d 记录=%s" % (i,U[i],V[i],WID[i],
      " ".join("%d"%x for x in struct.unpack_from("<8h",vf3,0xD0+i*16))))
# 量伽在图集里的实际墨迹列范围（相对 U），用 40 宽窗口
seg = al[V[i]:V[i]+28, U[i]:U[i]+40] > 32
c = np.nonzero(seg.any(axis=0))[0]
print("伽 相对 U 的墨迹列: %s" % ((int(c.min()),int(c.max())) if len(c) else None))
# ASCII 'A' 同样量
iA = CPS.index(ord("A"))
segA = al[V[iA]:V[iA]+28, U[iA]:U[iA]+40] > 32
cA = np.nonzero(segA.any(axis=0))[0]
print("A  idx=%d U=%d V=%d width=%d 墨迹列 %s" % (iA,U[iA],V[iA],WID[iA],
      (int(cA.min()),int(cA.max())) if len(cA) else None))
