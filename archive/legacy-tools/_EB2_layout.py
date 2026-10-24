import sys, os, struct
from collections import Counter
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
b = Vpp(os.path.join(G,"patch.vpp_pc")).read(Vpp(os.path.join(G,"patch.vpp_pc")).find("static_CH","le_strings"))
n = struct.unpack_from('<I', b, 8)[0]
print("count field =", n)
ents = [struct.unpack_from('<II', b, 16+i*8) for i in range(n)]
bad = [(i,s,l) for i,(s,l) in enumerate(ents) if l > 4000 or l < 1]
print("len 不在 [1,4000] 的条目:", len(bad))
for r in bad[:8]: print("   ", r)
ok = [e for e in ents if 1<=e[1]<=4000]
print("合理条目 %d, len 总和=%d, *2=%d" % (len(ok), sum(l for _,l in ok), sum(l for _,l in ok)*2))
print("文本区大小 =", len(b)-16-n*8)
print()
print("=== 目录前 24 条 ===")
for i in range(24): print("  [%3d] id=0x%08X len=%d" % (i, ents[i][0], ents[i][1]))
print("=== dirend 处的正文前 64 字节 ===")
dirend = 16+n*8
for off in range(dirend, dirend+64, 16):
    row = b[off:off+16]
    print("%06x  %-47s  %s" % (off, " ".join("%02x"%c for c in row), "".join(chr(c) if 32<=c<127 else "." for c in row)))
