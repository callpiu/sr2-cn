import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i, cp in enumerate(CPS)}
KEYS = ["three kings", "lawyer", "attorney", "defense", "king"]
for name in ("static_US", "static_CH"):
    for e in v.entries():
        if e["name"] != name: continue
        d = bytes(v.read(e))
        b, c, off_at, offs = file_offsets(d)
        print("=== %s ===" % name)
        for off in dict.fromkeys(offs):
            if not (0 < off <= len(d)-10): continue
            u, _ = read_units(d, off+8)
            if u is None: continue
            vals = [x for x, _ in u]
            if any(x in S for x in vals):
                t = "".join(S.get(x, chr(x) if 32 <= x < 127 else "?") for x in vals)
            else:
                t = "".join(chr(x) for x in vals)
            low = t.lower()
            if any(k in low for k in KEYS):
                print("  @%-9d %s" % (off, t[:110].replace("\n", " ")))
