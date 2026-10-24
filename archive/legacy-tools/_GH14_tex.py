# -*- coding: utf-8 -*-
import sys, os, hashlib, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "textures.vpp_pc"))
for e in v.entries():
    nm = (e["name"] or "")
    if not nm.startswith("fnt_"):
        continue
    raw = v.read(e)
    print("%-16s ext=%-8r size=%-9d md5=%s  head=%s" % (
        nm, e["ext"], len(raw), hashlib.md5(raw).hexdigest()[:12],
        " ".join("%02X" % c for c in raw[:16])))
