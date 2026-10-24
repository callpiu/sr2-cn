import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
d = bytes(v.read(v.find("static_CH","le_strings")))
b,c,off_at,offs = file_offsets(d)
print("=== 参考：同一记录在英文 static_US 里的内容 ===")
du = bytes(v.read(v.find("static_US","le_strings")))
bu,cu,ou,offu = file_offsets(du)
# 英文 static_US 的 charlist 是 ASCII，用直接映射
def dec_en(vals):
    return "".join(chr(x) if 0x20 <= x < 0x7f else "·" for x in vals)
for off in (93130, 299546):
    u,_ = read_units(du, off+8)
    if u: print("  @%d -> %r" % (off, dec_en([x for x,_ in u])))
print()
print("=== 汉化版里所有含 <img 的记录数量 ===")
n = 0
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    u,_ = read_units(d, off+8)
    if u is None: continue
    t = "".join(S.get(x,"·") for x,_ in u)
    if "<img" in t: n += 1
print("  含 <img 的记录: %d 条" % n)
print()
print("=== 「拆车厂」相关记录（前 12 条）===")
cnt = 0
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    u,_ = read_units(d, off+8)
    if u is None: continue
    vals = [x for x,_ in u]
    t = "".join(S.get(x,"·") for x in vals)
    if "拆车厂" in t:
        print("  @%-9d len=%-4d %s" % (off, len(vals), t[:80]))
        cnt += 1
        if cnt >= 12: break
