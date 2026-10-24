import sys, os, struct, bisect
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
d = bytes(v.read(v.find("static_CH","le_strings")))
b,c,off_at,offs = file_offsets(d)
uniq = sorted(set(o for o in offs if 0 < o <= len(d)-10))
T = 0x69AD7
i = bisect.bisect_right(uniq, T) - 1
print("包含 %d 的记录起点: %d (下一个 %d)" % (T, uniq[i], uniq[i+1] if i+1<len(uniq) else -1))
off = uniq[i]
u,_ = read_units(d, off+8)
if u:
    vals = [x for x,_ in u]
    t = "".join(S.get(x,"·") for x in vals)
    print("  记录长度 %d 槽位 (%d 字节)" % (len(vals), len(vals)*2))
    print("  文本: %s" % t[:200])
    print()
    # 里找「丈王」
    for k in range(len(t)-1):
        if t[k:k+2] == "丈王":
            print("  找到「丈王」@ 文本位置 %d" % k)
            print("    上下文: ...%s..." % t[max(0,k-30):k+30])
            print("    槽位值: %s" % vals[k:k+2])
    # 也找「三」
    for k,ch in enumerate(t):
        if ch == "三":
            print("  「三」@ %d: ...%s..." % (k, t[max(0,k-14):k+14]))
