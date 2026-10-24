import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(cn)}
d = bytes(v.read(v.find("static_CH","le_strings")))
b,c,oa,offs = file_offsets(d)
out = []
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    u,_ = read_units(d, off+8)
    if u is None: continue
    t = "".join(S.get(x,"·") for x,_ in u)
    if t.startswith("MARK-"):
        out.append((t.strip(), off, len(t)))
lines = ["%s  @%-9d len=%d" % (m, o, n) for m,o,n in sorted(out)]
open(r"F:\sr2-cn\_probe\mark_list.txt","w",encoding="utf-8").write("\n".join(lines))
print("标记清单（%d 条）:" % len(out))
for m,o,n in sorted(out):
    print("  %-12s @%-9d len=%d" % (m,o,n))
