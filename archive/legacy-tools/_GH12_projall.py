# -*- coding: utf-8 -*-
import sys, os, glob, hashlib
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
for vp in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    try:
        v = Vpp(vp)
    except Exception:
        continue
    for e in v.entries():
        if (e["ext"] or "") in ("vint_proj",) or "vint_proj" in ((e["name"] or "") + "." + (e["ext"] or "")):
            raw = v.read(e)
            print("[%s] %s.%s  %d B  md5=%s" % (
                os.path.basename(vp), e["name"], e["ext"], len(raw),
                hashlib.md5(raw).hexdigest()[:12]))
