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
U0 = 0xD0 + N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV = (len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
print("=== .cxt 里用到的中文字，在图集里是否有墨迹 ===")
s = open(G + r"\Mods\JUICED - Strings\juiced_CH.cxt", encoding="utf-8").read()
cjk = sorted({c for c in s if 0x100 < ord(c) < 0x9FFF})
noink = []
for ch in cjk:
    cp = ord(ch)
    if cp not in CPS:
        noink.append((ch, "不在表里")); continue
    i = CPS.index(cp)
    x, y = U[i], V[i]
    if not (0 <= x < 2048 and 0 <= y < 2048):
        noink.append((ch, "坐标越界 %d,%d" % (x,y))); continue
    ink = int((al[y:y+28, x:x+17] > 32).sum())
    if ink < 20:
        noink.append((ch, "墨迹仅 %d (U=%d,V=%d,idx=%d)" % (ink,x,y,i)))
print("  共 %d 个中文字，无墨迹的 %d 个:" % (len(cjk), len(noink)))
for ch, why in noink: print("     %s : %s" % (ch, why))
print()
print("=== 抽查几个 ===")
for ch in "伽马阴影过滤着色器":
    if ord(ch) not in CPS: print("  %s 不在表" % ch); continue
    i = CPS.index(ord(ch)); x,y = U[i], V[i]
    ink = int((al[y:y+28, x:x+17] > 32).sum())
    print("  %s idx=%-5d (U=%4d,V=%3d) 墨迹 %3d %s" % (ch, i, x, y, ink, "OK" if ink>20 else "★无"))
