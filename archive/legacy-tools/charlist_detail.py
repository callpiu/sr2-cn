import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
print("总项数 %d" % len(cn))
print()
print("前 100 个码点:")
for i in range(0, 100, 10):
    seg = cn[i:i+10]
    print("  [%3d..%3d] %s" % (i, i+9, " ".join("%s(%02X)" % (chr(c) if 32<=c<127 else "·", c) for c in seg)))
print()
# 找 '一' 的实际索引
for ch in "一二三四五你弟们":
    cp = ord(ch)
    if cp in cn:
        i = cn.index(cp)
        print("  %s U+%04X 索引 %d (十进制)   slot %d" % (ch, cp, i, i+0x20))
    else:
        print("  %s 不在表内" % ch)
print()
# 检查索引与码点是否单调
mono = sum(1 for i in range(1,len(cn)) if cn[i] > cn[i-1])
print("码点递增位置: %d / %d" % (mono, len(cn)-1))
