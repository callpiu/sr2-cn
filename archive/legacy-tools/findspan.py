import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
SLOTS = set(S)
d = bytes(v.read(v.find("static_CH","le_strings")))
b,c,off_at,offs = file_offsets(d)
T = 0x69AD7
# 遍历所有记录，检查 T 是否在其文本范围内
print("检查每条记录的实际文本范围（用 read_units 的 end）...")
found = []
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    u,end = read_units(d, off+8)
    if u is None: continue
    # 文本范围 off+8 .. end
    if off+8 <= T < end:
        found.append((off, end, len(u)))
print("包含 %d 的记录: %s" % (T, found))
print()
for off, end, ln in found:
    u,_ = read_units(d, off+8)
    vals = [x for x,_ in u]
    t = "".join(S.get(x,"·") for x in vals)
    print("  @%d  文本范围 %d..%d (%d 槽位)" % (off, off+8, end, ln))
    print("    完整文本(%d 字): %s" % (len(t), t))
