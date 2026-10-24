import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
N = struct.unpack_from("<i", vf3, 0x08)[0]
# 搜索形如 1,32,63,94,125,156,187... 的 int 序列（U 数组真起点）
target = [1+31*k for k in range(12)]
pat = b"".join(struct.pack("<i", t) for t in target)
found = []
for off in range(0xD0, len(vf3)-len(pat), 4):
    if vf3[off:off+len(pat)] == pat:
        found.append(off)
print("U 数组候选起点(搜索 1,32,63,...):", found)
# 也搜 156,187,218...（我当前读到的）
target2 = [155+31*k for k in range(12)]
pat2 = b"".join(struct.pack("<i", t) for t in target2)
found2 = [off for off in range(0xD0, len(vf3)-len(pat2), 4) if vf3[off:off+len(pat2)]==pat2]
print("当前读到的 156,187,218... 起点:", found2)
print()
print("0xD0 + N*16 =", 0xD0+N*16, " = 0x%X"%(0xD0+N*16))
for f in found:
    print("  候选 0x%X (%d)  相对 0xD0+N*16 差 %+d" % (f,f,f-(0xD0+N*16)))
# 检查 V 数组：真实 U 起点之后的 N*4
for f in found[:3]:
    vstart = f + N*4
    print("  若 U@0x%X → V@0x%X, V[0..5]=" % (f, vstart),
          list(struct.unpack_from("<6i", vf3, vstart)))
