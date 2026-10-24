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
def find_strs(addr, span=0x400):
    """在地址附近寻找 UTF-16 可读字符串"""
    m = read_mem(addr, span)
    if not m: return []
    s = m.decode("utf-16-le", "ignore")
    # 提取连续可打印片段
    import re
    out = []
    for mm in re.finditer(r'[\x20-\x7E\u4e00-\u9fff]{6,80}', s):
        out.append((addr+mm.start()*2, mm.group()))
    return out[:12]
for label, addr in (("崩溃帧 [ebp+04]", 0x580D8380),
                    ("堆对象 2", 0x5828FE40),
                    ("堆对象 3", 0x58272AD0),
                    ("堆对象 4", 0x580D83C0)):
    print("=== %s @ 0x%08X ===" % (label, addr))
    print("  头 32 字节: %s" % (read_mem(addr,32) or b"<不可读>").hex(" "))
    ss = find_strs(addr, 0x600)
    if ss:
        for a,s in ss[:8]:
            print("    0x%08X  %r" % (a, s))
    else:
        print("    （无可读字符串）")
    print()
