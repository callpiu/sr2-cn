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
U0 = 0xD0 + N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))
print("字节  -> 码点  -> 字表索引 -> slot  -> 图集(U,V) -> 墨量")
for byte in (0xB9, 0xBA, 0xC2, 0xF0):
    cp = byte
    i = CPS.index(cp) if cp in CPS else None
    if i is None: print("  0x%02X 不在字表" % byte); continue
    slot = i + 0x20
    x, y = U[i], V[i]
    ink = int((al[y:y+28, x:x+31] > 32).sum())
    print("  0x%02X %s -> U+%04X -> idx %-5d -> slot %-5d -> (%4d,%4d) 墨量 %d" % (
        byte, chr(cp), cp, i, slot, x, y, ink))
print()
# 善 的槽位
i = CPS.index(0x5584)
print("善 U+5584 -> idx %d -> slot %d -> (%d,%d)" % (i, i+0x20, U[i], V[i]))
ink = int((al[V[i]:V[i]+28, U[i]:U[i]+31] > 32).sum())
print("  墨量 %d" % ink)
print()
# 列出 图集里 slot 185 (idx 153) 那个字形长什么样
i = 153
x,y = U[i], V[i]
g = al[y:y+28, x:x+31]
Image.fromarray(255-g).resize((31*10, 28*10), Image.NEAREST).save(r"F:\sr2-cn\_juice_fix\glyph_idx153.png")
print("写出 glyph_idx153.png (slot 185, 字表说它是 U+00B9 ¹)")
i2 = CPS.index(0x5584)
g2 = al[V[i2]:V[i2]+28, U[i2]:U[i2]+31]
Image.fromarray(255-g2).resize((31*10, 28*10), Image.NEAREST).save(r"F:\sr2-cn\_juice_fix\glyph_shan.png")
print("写出 glyph_shan.png (slot %d, 善)" % (i2+0x20))
