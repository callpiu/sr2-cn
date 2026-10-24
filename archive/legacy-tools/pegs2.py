import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
for tag, p in (("修复后部署", os.path.join(G,"patch.vpp_pc")),
               ("第三方原始", os.path.join(r"F:\sr2-cn\_juice_fix","patch.vpp_pc")),
               ("原厂繁中",   os.path.join(r"F:\sr2-cn\pristine","patch.vpp_pc"))):
    v = Vpp(p)
    e = v.find("fnt_chinese","g_peg_pc")
    d = bytes(v.read(e))
    fmt = struct.unpack_from("<H", d, 0x20)[0]
    print("=== %s ===" % tag)
    print("  g_peg_pc %d 字节" % len(d))
    print("  PEG magic   = %r" % d[:4])
    print("  u16 @0x1C   = %d" % struct.unpack_from("<H", d, 0x1C)[0])
    print("  u16 @0x1E   = %d" % struct.unpack_from("<H", d, 0x1E)[0])
    print("  u16 @0x20   = %d  (格式码)" % fmt)
    print("  u32 @0x34   = %d" % struct.unpack_from("<I", d, 0x34)[0])
    print("  非零字节 %.1f%%" % (100*sum(1 for b in d[:65536] if b)/65536))
print()
# 查 pegs.vpp_pc 里的描述符（第三方与原厂）
for tag, pep in (("游戏目录", os.path.join(G,"pegs.vpp_pc")),):
    v = Vpp(pep)
    e = v.find("fnt_chinese","peg")
    if e:
        d = bytes(v.read(e))
        print("=== pegs.vpp_pc 里 fnt_chinese.peg (%d 字节) ===" % len(d))
        print("  前 40 字节: %s" % d[:40].hex(' '))
        print("  u16 @0x1C W = %d" % struct.unpack_from("<H", d, 0x1C)[0])
        print("  u16 @0x1E H = %d" % struct.unpack_from("<H", d, 0x1E)[0])
        print("  u16 @0x20 F = %d" % struct.unpack_from("<H", d, 0x20)[0])
        print("  u32 @0x34 S = %d" % struct.unpack_from("<I", d, 0x34)[0])
