# -*- coding: utf-8 -*-
import sys, os, glob, struct, hashlib
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
TARGETS = (0xF284ED87, 0xAF10621E)

print("=== 1) 所有 VPP 里的 static_CH ===")
for vp in sorted(glob.glob(os.path.join(G, "**", "*.vpp_pc"), recursive=True)):
    try:
        v = Vpp(vp)
    except Exception as ex:
        print("  [跳过] %s (%s)" % (os.path.basename(vp), ex)); continue
    for e in v.entries():
        nm = (e["name"] or "")
        if "static_CH" in nm:
            raw = v.read(e)
            hits = []
            for t in TARGETS:
                p = raw.find(struct.pack(">I", t))
                hits.append("0x%08X@%s" % (t, p if p >= 0 else "-"))
            print("  [%s] %s.%s  %d B  md5=%s  %s" % (
                os.path.relpath(vp, G), nm, e["ext"], len(raw),
                hashlib.md5(raw).hexdigest()[:12], " ".join(hits)))

print("\n=== 2) 松散 static_CH / dlc_ch ===")
for pat in ("**/static_CH*", "**/dlc_ch*", "**/*ch*.le_strings"):
    for p in glob.glob(os.path.join(G, pat), recursive=True):
        b = open(p, "rb").read()
        hits = ["0x%08X@%s" % (t, b.find(struct.pack(">I", t))) for t in TARGETS]
        print("  %-60s %8d B  %s" % (os.path.relpath(p, G), len(b), " ".join(hits)))
