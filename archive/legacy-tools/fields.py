import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
W = r"F:\sr2-cn"
for tag, p in (("第三方", os.path.join(W,"_juice_fix","patch.vpp_pc")),
               ("原厂繁中", os.path.join(W,"pristine","patch.vpp_pc"))):
    v = Vpp(p)
    vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
    N = struct.unpack_from("<i",vf3,0x08)[0]
    CH0 = 0xD0
    print("=== %s (N=%d) 记录区起点 0x%X ===" % (tag, N, CH0))
    print("%-4s %-6s %s" % ("#","字符","16 字节原始数据 (i16 x8)"))
    CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    for i in list(range(0,6))+list(range(33,38))+list(range(78,82)):
        rec = struct.unpack_from("<8h", vf3, CH0+i*16)
        ch = chr(CPS[i]) if i < len(CPS) else "?"
        print("%-4d %-6r %s" % (i, ch, " ".join("%6d"%x for x in rec)))
    print()
    # 统计所有 ASCII 记录的字段分布
    import collections
    f0=collections.Counter(); f3=collections.Counter(); f6=collections.Counter()
    for i in range(min(95,N)):
        r = struct.unpack_from("<8h", vf3, CH0+i*16)
        f0[r[0]]+=1; f3[r[3]]+=1; f6[r[6]]+=1
    print("  ASCII 区字段分布:")
    print("    +0x00 : %s" % dict(f0))
    print("    +0x06 : %s" % dict(f3))
    print("    +0x0C : %s" % dict(f6))
    print()
