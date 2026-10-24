import os, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
H1, H2 = 0x84F287ED, 0x10AF1E62
p = os.path.join(G,"patch.vpp_pc")
v = Vpp(p)
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
d = bytes(v.read(v.find("static_CH","le_strings")))
b,c,oa,offs = file_offsets(d)
print("count=%d, 唯一偏移 %d 个" % (c, len(set(offs))))
print()
# 记录头是 8 字节：off+0..off+3 = ?, off+4..off+7 = ?  文本从 off+8
print("=== 前 5 条记录的头 8 字节 ===")
for off in list(dict.fromkeys(offs))[:5]:
    print("  @%-9d 头8: %s   dword0=%08X dword1=%08X" % (off, d[off:off+8].hex(" "),
          struct.unpack_from("<I",d,off)[0], struct.unpack_from("<I",d,off+4)[0]))
print()
# 找目标 hash：可能在 off 或 off+4，按不同字节序试
found = 0
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    hdr = d[off:off+8]
    cands = []
    for base in (0,4):
        for endian in ("<",">"):
            v0, = struct.unpack_from(endian+"H", d, off+base)
            v1, = struct.unpack_from(endian+"H", d, off+base+2)
            cands.append((v0<<16)|v1)
            cands.append((v1<<16)|v0)
    if H1 in cands or H2 in cands:
        u,end = read_units(d, off+8)
        if u is None: continue
        vals = [x for x,_ in u]
        t = "".join(S.get(x,"\uFFFD") for x in vals)
        h = H1 if H1 in cands else H2
        print("=== hash 0x%08X @%d ===" % (h, off))
        print("  头: %s" % hdr.hex(" "))
        print("  len=%d  文本: %s" % (len(vals), t))
        print("  槽位: %s" % vals)
        print("  槽位->(索引,字): %s" % [(x, x-0x20, S.get(x,"?")) for x in vals])
        print()
        found += 1
print("找到 %d 条" % found)
