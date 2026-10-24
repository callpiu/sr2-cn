import struct, os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
p = os.path.join(G,"juiced","CrashDumps","SR2_pc.exe.20261010222959.dmp")
d = open(p,"rb").read()
sig, ver, nstreams, rva, flags = struct.unpack_from("<IIIII", d, 0)
streams = {}
for i in range(nstreams):
    st, sz, r = struct.unpack_from("<III", d, rva + i*12)
    streams[st] = (sz, r)
# MemoryListStream = 5
sz, r = streams[5]
n = struct.unpack_from("<I", d, r)[0]
print("MemoryListStream: %d 个内存块" % n)
blocks = []
for i in range(n):
    addr, size, rva2 = struct.unpack_from("<QII", d, r + 4 + i*16)
    blocks.append((addr, size, rva2))
total = sum(b[1] for b in blocks)
print("  总覆盖 %d 字节 (%.1f MB)" % (total, total/1048576))
print("  前 15 块:")
for a,s,rr in blocks[:15]:
    print("    0x%08X .. 0x%08X  (%d 字节)" % (a, a+s, s))
print()
# 找崩溃地址 0x00CAD24E 所在块
TARGET = 0x00CAD24E
for a,s,rr in blocks:
    if a <= TARGET < a+s:
        print("崩溃地址 0x%X 在块 0x%X..0x%X (文件偏移 0x%X)" % (TARGET, a, a+s, rr))
        off = rr + (TARGET - a)
        ctx = d[off-40:off+40]
        print("  崩溃点前后 80 字节: %s" % ctx.hex(" "))
        break
else:
    print("崩溃地址不在任何内存块里")
