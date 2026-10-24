import sys, os
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def get(p, name, ext):
    v = Vpp(p); return v.read(v.find(name, ext))
mine = get(os.path.join(G,"patch.vpp_pc"),"fnt_chinese","g_peg_pc")
offi = get(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig","fnt_chinese","g_peg_pc")
print("sizes:", len(mine), len(offi))
# mine 是不是 official 去掉前 H 字节？
for H in (0x40,0x80,0x100,0x140,0x200,0x400):
    n = min(len(mine), 4096)
    same = sum(1 for i in range(n) if mine[i] == offi[i+H])
    print("  H=0x%03X: 前4KB相同字节=%d/%d" % (H, same, n))
print()
print("官方 peg 前 256 字节:")
for o in range(0, 256, 16):
    row = offi[o:o+16]
    print("  +%03X  %s" % (o, " ".join("%02x"%c for c in row)))
print()
print("官方 peg +0x100 起 64 字节:", offi[0x100:0x140].hex())
print("我的 peg +0x000 起 64 字节:", mine[0:64].hex())
print("我的 peg +0x0FC 起 64 字节:", mine[0xFC:0x13C].hex())
