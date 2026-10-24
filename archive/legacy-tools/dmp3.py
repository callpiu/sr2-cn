import struct, os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
p = os.path.join(G,"juiced","CrashDumps","SR2_pc.exe.20261010222959.dmp")
d = open(p,"rb").read()
sig, ver, nstreams, rva, flags = struct.unpack_from("<IIIII", d, 0)
streams = {}
for i in range(nstreams):
    st, sz, r = struct.unpack_from("<III", d, rva + i*12)
    streams[st] = (sz, r)
sz, r = streams[5]
n = struct.unpack_from("<I", d, r)[0]
blocks = []
for i in range(n):
    a, s, rr = struct.unpack_from("<QII", d, r + 4 + i*16)
    blocks.append((a, s, rr))
def read_mem(addr, ln):
    for a,s,rr in blocks:
        if a <= addr and addr+ln <= a+s:
            o = rr + (addr-a)
            return d[o:o+ln]
    return None
EBP = 0x152AF6B4
print("=== 崩溃帧关键局部变量 ===")
for delta, nm in ((-0x1C,"字符串指针 [ebp-1C]"), (-0x0C,"EDI/计数 [ebp-0C]"), (-0x14,"[ebp-14]"), (-0x24,"[ebp-24]")):
    m = read_mem(EBP+delta, 4)
    if m:
        v = struct.unpack("<I", m)[0]
        print("  %-22s = 0x%08X (%d)" % (nm, v, v))
print()
print("=== 崩溃帧上下 64 字节 ===")
m = read_mem(EBP-64, 128)
if m:
    for i in range(0, 128, 16):
        vals = struct.unpack_from("<4I", m, i)
        print("  0x%08X: %s" % (EBP-64+i, " ".join("%08X"%x for x in vals)))
print()
# 看 0x1 附近是否真的不可读；看调用者栈帧
print("=== 调用者帧（EBP+8 起的返回地址链）===")
for i in range(0, 8):
    m = read_mem(EBP + 4 + i*4, 4)
    if m:
        v = struct.unpack("<I", m)[0]
        print("  [ebp+%02X] = 0x%08X" % (4+i*4, v))
