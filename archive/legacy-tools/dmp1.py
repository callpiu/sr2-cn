import struct, os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
p = os.path.join(G,"juiced","CrashDumps","SR2_pc.exe.20261010222959.dmp")
d = open(p,"rb").read()
print("dmp %d 字节" % len(d))
print("magic: %r" % d[:4])
sig, ver, nstreams, rva, flags = struct.unpack_from("<IIIII", d, 0)
print("  Signature=0x%X Version=0x%X 流数=%d 目录RVA=0x%X Flags=0x%X" % (sig,ver,nstreams,rva,flags))
print()
# 遍历流目录
print("=== 流目录 ===")
for i in range(nstreams):
    st, sz, r = struct.unpack_from("<III", d, rva + i*12)
    print("  #%-3d type=0x%08X size=%-10d rva=0x%X" % (i, st, sz, r))
