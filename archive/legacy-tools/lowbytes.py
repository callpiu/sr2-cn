import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
print("字表 %d 项" % len(CPS))
print()
print("=== 码点 0x80..0xFF 在字表里的位置（slot = 索引+0x20）===")
for cp in range(0x80, 0x100):
    if cp in CPS:
        i = CPS.index(cp)
        print("  U+%04X %-3s 索引 %-5d slot %-5d" % (cp, chr(cp), i, i+0x20), end="")
        if cp % 3 == 2: print()
print()
print()
print("=== 屏幕上的乱码字符是否在字表里 ===")
screen = "¹ºÂð·²û¿ÉÕÖ»ñµÃªñ¹£Õë"
for ch in screen:
    cp = ord(ch)
    if cp in CPS:
        i = CPS.index(cp)
        print("  %s U+%04X 索引 %-5d slot %-5d  -> 字表里的字: %s" % (ch, cp, i, i+0x20, chr(CPS[CPS.index(cp)])))
    else:
        print("  %s U+%04X 不在字表里" % (ch, cp))
