import sys, struct
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
print("N =", N, "len =", len(vf3))
print("\n0xD0 起前 128 字节（假设 16B/条）:")
for i in range(8):
    o = 0xD0 + i*16
    print("  idx%-3d %s" % (i, " ".join("%02X"%b for b in vf3[o:o+16])))
# 试各种记录大小，找 U/V 数组起点
for rec in (12,16,20,24):
    u0 = 0xD0 + N*rec
    rest = len(vf3)-u0
    print("rec=%d  U0=%d  剩余=%d  = %.2f 项" % (rec, u0, rest, rest/4))
