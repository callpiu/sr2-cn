import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
sl = lambda ch: CPS.index(ord(ch))+0x20
print("三 slot=%d, 王 slot=%d, 丈 slot=%d" % (sl("三"), sl("王"), sl("丈")))
d = bytes(v.read(v.find("static_CH","le_strings")))
b,c,off_at,offs = file_offsets(d)
# 遍历所有记录，检查是否有连续槽位 271,1796（三王）或 270,1796（丈王）
print()
print("=== 记录里出现 (271,1796) 或 (270,1796) 的位置 ===")
n=0
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    u,_ = read_units(d, off+8)
    if u is None: continue
    vals = [x for x,_ in u]
    for k in range(len(vals)-1):
        if vals[k] in (270,271) and vals[k+1]==1796:
            t = "".join(S.get(x,"·") for x in vals)
            print("  @%-9d 位置 %d: 槽位 (%d,%d) = %r%r  文本: ...%s..." % (
                off, k, vals[k], vals[k+1], S.get(vals[k]), S.get(1796),
                t[max(0,k-20):k+22].replace("\n"," ")))
            n+=1
print("  共 %d 处" % n)
