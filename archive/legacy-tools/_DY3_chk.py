import sys, os
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def cl(p):
    v = Vpp(p); e = v.find("charlist_CH","txt")
    t = v.read(e).decode('utf-8','replace').replace('\r','').split('\n')
    return [int(s) for s in t if s.strip().isdigit()]
nums_M = cl(os.path.join(G,"patch.vpp_pc"))
nums_O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")
WRONG = [0x4EFB,0x74CF,0x5076,0x5DE7,0x4F4D,0x96C4,0x8861]
RIGHT = [0x4F60,0x7684,0x5F1F,0x5144,0x4EEC,0x9700,0x8981]
for cp in WRONG+RIGHT:
    ch = chr(cp)
    im = nums_M.index(cp) if cp in nums_M else None
    io = nums_O.index(cp) if cp in nums_O else None
    print("U+%04X %s  my_idx=%-5s official_idx=%-5s" % (cp, ch, im, io))
