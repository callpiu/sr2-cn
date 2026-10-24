# -*- coding: utf-8 -*-
import sys, os, glob, struct, hashlib, re
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
        nm = (e["name"] or "")
        if re.search(r"^(jap|ige_)", nm, re.I):
            raw = v.read(e)
            extra = ""
            if (e["ext"] or "") == "vf3_pc" and len(raw) >= 12:
                extra = " N=%d" % struct.unpack_from("<I", raw, 8)[0]
            elif raw[:4] == b"GEKV":
                extra = " size=%d dim=%dx%d" % (
                    struct.unpack_from("<I", raw, 0x0C)[0],
                    struct.unpack_from("<H", raw, 0x1C)[0],
                    struct.unpack_from("<H", raw, 0x1E)[0])
                ss = [m.group().decode() for m in re.finditer(rb"[\x20-\x7e]{4,}", raw)]
                extra += " tga=%s" % (ss[-1:] if ss else [])
            print("[%-16s] %-16s.%-9s %9d B md5=%s%s" % (
                os.path.basename(vp), nm, e["ext"], len(raw), hashlib.md5(raw).hexdigest()[:10], extra))
