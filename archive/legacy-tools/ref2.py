import sys, os
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS=[int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S={i+0x20:chr(cp) for i,cp in enumerate(CPS)}
d=bytes(v.read(v.find("static_CH","le_strings")))
b,c,oa,offs=file_offsets(d)
def dec(vals): return "".join(S.get(x, chr(x) if 32<=x<127 else "\uFFFD") for x in vals)
recs={}
for off in dict.fromkeys(offs):
    if not (0<off<=len(d)-10): continue
    r=read_units(d,off+8)
    if not r: continue
    recs[off]=[x for x,_ in r[0]]
for off in (225978, 279274):
    if off in recs:
        print("@%-8d %r" % (off, dec(recs[off])))
        print("          槽位 %s" % recs[off])
print()
for kw in ("老斯蒂尔","斯蒂尔沃特","郊区","辩护","律师"):
    hits=[(o,dec(v)) for o,v in recs.items() if kw in dec(v)]
    print("含 %-6s 的记录 %d 条" % (kw, len(hits)))
    for o,t in hits[:4]:
        print("    @%-8d %r" % (o,t[:60]))
