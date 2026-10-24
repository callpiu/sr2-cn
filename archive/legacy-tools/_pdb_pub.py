# -*- coding: utf-8 -*-
"""解析 PUB32 记录得到符号 RVA。
PUB32 payload: flags(u32) offset(u32) segment(u16) name(u32)
需要 section header 表把 (segment, offset) 转成 RVA。
DBI stream 里段头紧跟 header（headerSize）。段头 40 字节/个，含 VirtualAddress。
"""
import sys, struct, pickle
sys.stdout.reconfigure(encoding="utf-8")
P = r"G:\SteamLibrary\steamapps\common\Saints Row 2\DFEngine.pdb"
d = open(P, "rb").read()
info = pickle.load(open(r"F:\sr2-cn\_pdb_dir.pkl", "rb"))
BS = info["BS"]; sizes = info["sizes"]; blocks = info["blocks"]


def stream(i):
    return b"".join(d[b * BS:(b + 1) * BS] for b in blocks[i])[:sizes[i]]


s3 = stream(3)
u32 = lambda b, o: struct.unpack("<I", b[o:o + 4])[0]
u16 = lambda b, o: struct.unpack("<H", b[o:o + 2])[0]
hdrSize = u32(s3, 4)
print("DBI headerSize =", hdrSize)
# DBI 头后紧跟 mods(?) 然后 section headers。标准布局：
# +0 sig, +4 version, +8 age, +12 gsStream(u16), +14 pssStream(u16), +16 symStream(u16)
# +18 ??, ... 之后是 optional debug header (6*u16) 和 EC info 等
# 简化：section header 计数在 DBI 头里。
print("DBI header hex 0..64:", s3[:64].hex(" "))
# 试从 hdrSize 处读 section headers
segs = []
off = hdrSize
for k in range(16):
    if off + 40 > len(s3):
        break
    ent = s3[off:off + 40]
    name = ent[0:8].rstrip(b"\x00").decode("ascii", "replace")
    VA = u32(ent, 8)
    sz = u32(ent, 12)
    if name and 0x10000000 <= VA < 0x12000000:
        segs.append((k + 1, name, VA, sz))
        print("  seg %2d %-10s VA=0x%08X size=0x%X" % (k + 1, name, VA, sz))
    off += 40
    if len(segs) >= 8:
        break

pickle.dump(segs, open(r"F:\sr2-cn\_pdb_segs.pkl", "wb"))
