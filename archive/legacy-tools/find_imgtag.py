import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
print("=== 含 <img ...chopshop...> 的记录 ===")
for e in v.entries():
    if e["ext"] not in ("le_strings",""): continue
    try: b,c,off_at,offs = file_offsets(bytes(v.read(e)))
    except Exception: continue
    d = bytes(v.read(e))
    n = 0
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        u,_ = read_units(d, off+8)
        if u is None: continue
        vals = [x for x,_ in u]
        t = "".join(S.get(x,"·") for x in vals)
        if "img" in t.lower() and "chopshop" in t.lower():
            print("  %-16s @%-9d %s" % (e["name"], off, t[:110]))
            n += 1
            if n >= 8: break
