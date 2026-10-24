import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
def dec(vals): return "".join(S.get(x,"·") for x in vals)
# 搜所有 le_strings 条目（包括非 CH 的）
print("=== 在所有 le_strings 里找含「王」的短记录（≤6字）===")
for e in v.entries():
    if e["ext"] != "le_strings": continue
    d = bytes(v.read(e))
    try:
        b,c,oa,offs = file_offsets(d)
    except Exception:
        continue
    hits = []
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        u,_ = read_units(d, off+8)
        if u is None: continue
        vals = [x for x,_ in u]
        t = dec(vals)
        if 1 <= len(t) <= 6 and "王" in t:
            hits.append((off, t, vals))
    if hits:
        print("  %-24s %d 条:" % (e["name"], len(hits)))
        for off,t,vals in hits[:6]:
            print("      @%-8d %-8s 槽位 %s" % (off, t, vals))
