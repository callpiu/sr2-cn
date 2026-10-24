import struct, os, re
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
def find_strs(addr, span=0x600):
    m = read_mem(addr, span)
    if not m: return []
    s = m.decode("utf-16-le", "ignore")
    out = []
    for mm in re.finditer(r'[\x20-\x7E\u4e00-\u9fff]{6,80}', s):
        out.append((addr+mm.start()*2, mm.group()))
    return out[:10]
for label, addr in (("崩溃帧[ebp+04]", 0x580D8380),
                    ("堆对象B", 0x5828FE40),
                    ("堆对象C", 0x58272AD0)):
    print("=== %s @ 0x%08X ===" % (label, addr))
    h = read_mem(addr, 32)
    print("  头32字节: %s" % (h.hex(" ") if h else "N/A"))
    ss = find_strs(addr)
    if ss:
        for a,s in ss[:8]:
            print("    0x%08X  %r" % (a, s))
    else:
        print("    无可读字符串")
    print()
