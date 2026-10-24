import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def get(p, name, ext):
    v = Vpp(p); return v.read(v.find(name, ext))
M = get(os.path.join(G, "patch.vpp_pc"), "fnt_chinese", "vf3_pc")
O = get(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "fnt_chinese", "vf3_pc")
print("len mine=%d  official=%d" % (len(M), len(O)))
print()
for off in range(0, 0xBC, 4):
    vm = struct.unpack_from("<I", M, off)[0]
    vo = struct.unpack_from("<I", O, off)[0]
    flag = "   <<< 不同" if vm != vo else ""
    print("  +0x%02X  mine=%-12d  official=%-12d%s" % (off, vm, vo, flag))
print()
print("尾部(os.path 前的可打印串):")
for tag, b in (("mine", M), ("official", O)):
    i = 0x20
    while i < 0xBC:
        j = i
        while j < 0xBC and 32 <= b[j] < 127:
            j += 1
        if j - i >= 3:
            print("   %-9s @0x%02X: %r" % (tag, i, b[i:j].decode("ascii")))
        i = j + 1
