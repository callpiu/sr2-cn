# -*- coding: utf-8 -*-
"""DLC le_strings 解析（按实际小端字节序校准）。
   已知：0x00 magic=0x737F4CA8  0x08 = N(条目数)
   逐个偏移试探，找出正确布局。"""
import sys, os, struct
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
d = open(os.path.join(G, "DLC", "Text", "dlc_ch.le_strings"), "rb").read()
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in
       v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
slot2ch = {i + 0x20: chr(c) for i, c in enumerate(cps)}

print("size=%d" % len(d))
print("前 0x30 字节 hex:")
for o in range(0, 0x30, 16):
    print("  0x%02X: %s   |%s|" % (o, d[o:o + 16].hex(" "),
          "".join(chr(b) if 32 <= b < 127 else "." for b in d[o:o + 16])))

print("\n### 试探 N 的位置")
for o in (0x04, 0x08, 0x0C, 0x10):
    le = struct.unpack_from("<I", d, o)[0]
    be = struct.unpack_from(">I", d, o)[0]
    print("  0x%02X: LE=%-12d BE=%-12d" % (o, le, be))

# 记忆说 0x08 = N=982；实测该处 LE 读数
N_guess = struct.unpack_from("<I", d, 0x08)[0]
print("\n0x08 LE = %d  (若为 982 则布局成立)" % N_guess)
print("982*4 = %d ; 0x40C + 982*4 = 0x%X" % (982 * 4, 0x40C + 982 * 4))
print("982*4 + 0x1364 = 0x%X  (EOF=0x%X)" % (0x1364 + 982 * 4, len(d)))