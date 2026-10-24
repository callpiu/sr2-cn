import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
tot = 0
for e in v.entries():
    if e["ext"] not in ("le_strings",) and e["ext"] != "":
        continue
    d = bytes(v.read(e))
    try: b,c,off_at,offs = file_offsets(d)
    except Exception: continue
    hits = []
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        u,_ = read_units(d, off+8)
        if u is None: continue
        vals = [x for x,_ in u]
        t = "".join(S.get(x,"·") for x in vals)
        for w in ("三王","丈王"):
            if w in t:
                k = t.index(w)
                hits.append((off, w, t[max(0,k-30):k+30].replace("\n"," "), vals[k:k+2]))
    if hits:
        print("=== %s ===" % e["name"])
        for off,w,ctx,sv in hits[:5]:
            print("  @%-9d %s  %s" % (off, w, ctx))
            print("            槽位 %s" % sv)
        tot += len(hits)
print()
print("合计命中 %d 处" % tot)
