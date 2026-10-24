import os, struct
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
p = os.path.join(G, "SR2_pc.exe")
d = open(p, "rb").read()
e_lfanew = struct.unpack_from("<I", d, 0x3c)[0]
assert d[e_lfanew:e_lfanew+4] == b"PE\0\0"
coff = e_lfanew + 4
nsec, = struct.unpack_from("<H", d, coff+2)
optsz, = struct.unpack_from("<H", d, coff+16)
opt = coff + 20
magic, = struct.unpack_from("<H", d, opt)
ib, = struct.unpack_from("<I", d, opt+28)
print(f"magic={magic:#x} ImageBase={ib:#x} nsec={nsec}")
sec = opt + optsz
secs = []
for i in range(nsec):
    o = sec + i*40
    name = d[o:o+8].rstrip(b"\0").decode()
    vsz, va, rsz, rp = struct.unpack_from("<IIII", d, o+8)
    secs.append((name, va, vsz, rp, rsz))
    print(f"  {name:8s} VA={va:#010x} vsz={vsz:#010x} raw={rp:#010x} rsz={rsz:#010x}")
print()
# 目标池 RVA（.rdata 内 raw 0x9e0fc0 -> 用段表换算）
T = 0x9e0f80
for name, va, vsz, rp, rsz in secs:
    if rp <= T < rp + rsz:
        rva = T - rp + va
        print(f"池文件偏移 {T:#x} 位于 {name}, RVA={rva:#x}, VA={rva+ib:#x}")
        break
print()
lo, hi = 0x9e0f00, 0x9e1100
hits = []
for off in range(0, len(d)-4, 4):
    v, = struct.unpack_from("<I", d, off)
    if lo <= v <= hi:
        hits.append((off, v, "RVA"))
for off in range(0, len(d)-4, 4):
    v, = struct.unpack_from("<I", d, off)
    if lo+ib <= v <= hi+ib:
        hits.append((off, v, "VA"))
print("指向池附近的 4 字节指针命中数 =", len(hits))
for off, v, tag in hits[:40]:
    print(f"  @{off:#x} -> {v:#x} ({tag})")
