import os, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
H1, H2 = 0x84F287ED, 0x10AF1E62
v = Vpp(r"F:\sr2-cn\_probe\patch_probe_marks.vpp_pc")
d = bytes(v.read(v.find("static_CH","le_strings")))
b,c,oa,offs = file_offsets(d)
print("=== 标记后的文件里，那两条记录的内容 ===")
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    cands = []
    for base in (0,4):
        for endian in ("<",">"):
            if off+base+4 > len(d): continue
            v0, = struct.unpack_from(endian+"H", d, off+base)
            v1, = struct.unpack_from(endian+"H", d, off+base+2)
            cands += [(v0<<16)|v1, (v1<<16)|v0]
    h = H1 if H1 in cands else (H2 if H2 in cands else None)
    if h is None: continue
    u,_ = read_units(d, off+8)
    t = "".join(chr(x) if 0x20<=x<0x7f else "?" for x,_ in u)
    print("  hash 0x%08X @%-9d -> %r" % (h, off, t[:44]))
print()
# 统计 ASCII 标记数量
n = 0
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    u,_ = read_units(d, off+8)
    if u is None: continue
    t = "".join(chr(x) for x,_ in u)
    if t.startswith("MARK-"): n += 1
print("  含 MARK- 标记的记录: %d 条" % n)
