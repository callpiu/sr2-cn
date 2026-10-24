import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
print("律 slot=%d, 延 slot=%d, 三 slot=%d, 丈 slot=%d" % (
    CPS.index(0x5F8B)+0x20, CPS.index(0x5EF6)+0x20, CPS.index(0x4E09)+0x20, CPS.index(0x4E08)+0x20))
print()
# 找所有含「辩护」的记录
for e in v.entries():
    if e["ext"] not in ("le_strings","") : continue
    try: b,c,off_at,offs = file_offsets(bytes(v.read(e)))
    except Exception: continue
    d = bytes(v.read(e))
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        u,_ = read_units(d, off+8)
        if u is None: continue
        vals = [x for x,_ in u]
        t = "".join(S.get(x,"·") for x in vals)
        if "辩护" in t or "指定" in t and "师" in t:
            k = t.find("辩护") if "辩护" in t else 0
            print("  %-16s @%-9d %s" % (e["name"], off, t[max(0,k-14):k+30].replace("\n"," ")))
            print("       槽位: %s" % vals[max(0,k-4):k+8])
