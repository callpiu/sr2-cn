# -*- coding: utf-8 -*-
import sys, os, glob, struct, hashlib
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
print("=== 所有 VPP 里的 vf3_pc 条目 ===")
for vp in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    try:
        v = Vpp(vp)
    except Exception:
        continue
    for e in v.entries():
        if (e["ext"] or "") == "vf3_pc":
            raw = v.read(e)
            N = struct.unpack_from("<I", raw, 8)[0] if len(raw) >= 12 else -1
            print("  [%-18s] %s.%s  %d B  N=%d  md5=%s" % (
                os.path.basename(vp), e["name"], e["ext"], len(raw), N,
                hashlib.md5(raw).hexdigest()[:10]))
