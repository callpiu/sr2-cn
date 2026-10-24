import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import CharList, file_offsets, read_units, decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
CL = CharList(CPS)
# 看 static_CH 的结构：记录头是什么
d = bytes(v.read(v.find("static_CH","le_strings")))
print("static_CH %d 字节, 前 32 字节: %s" % (len(d), d[:32].hex(" ")))
b,c,oa,offs = file_offsets(d)
offs_u = list(dict.fromkeys(offs))
print("记录数 %d, 文件头 b=%d c=%d oa=%d" % (len(offs_u), b, c, oa))
print()
# 取一条记录看结构
off = sorted(o for o in offs_u if 0 < o <= len(d)-10)[3]
print("记录 @%d 原始字节: %s" % (off, d[off:off+28].hex(" ")))
u,_ = read_units(d, off+8)
print("  解码: %r" % decode(u, CL))
print()
# 这两个 key 是否在表里（以 key hash 形式）？先看记录头两个 u32
import struct
h = struct.unpack_from("<II", d, off)
print("  记录头 u32 x2 = 0x%08X 0x%08X" % h)
# 搜 SUI_OPTIONS_TITLE 的 DJB2 hash 是常见做法，但也可能明文
print()
print("=== 表里有没有明文 SUI_ ===")
for k in (b"SUI_OPTIONS_TITLE", b"SUI_LOADING_9", b"SUI_"):
    print("  %-24s %s" % (k.decode(), k in d))
