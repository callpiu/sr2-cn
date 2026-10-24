import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
def dec(vals): return "".join(S.get(x,"·") for x in vals)
TARGETS = ("Hoods","Gang_Names","HUD_text","MissionText","Activity_text","Menus_text","ActivityOther","ActivityCrime","ActivityCars","Item_text")
for nm in TARGETS:
    e = v.find(nm)
    if not e: 
        print("  %-16s 未找到" % nm); continue
    d = bytes(v.read(e))
    try:
        b,c,oa,offs = file_offsets(d)
    except Exception as ex:
        print("  %-16s 非 le_strings (%d 字节)" % (nm, len(d))); continue
    hits = []
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        u,_ = read_units(d, off+8)
        if u is None: continue
        vals = [x for x,_ in u]
        t = dec(vals)
        if 1 <= len(t) <= 8 and ("三" in t or "丈" in t or "王" in t):
            hits.append((off,t,vals))
    print("  %-16s (%d 字节) 命中 %d 条" % (nm, len(d), len(hits)))
    for off,t,vals in hits[:8]:
        print("       @%-8d %-10s 槽位 %s" % (off, t, vals))
