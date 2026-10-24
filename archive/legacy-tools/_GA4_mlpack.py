"""GA4: does the OFFICIAL multi-language patch ship Chinese fnt_body_n/s
(or a vint_proj) that our v10 patch dropped?
"""
import sys, os, glob, hashlib, re
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

CAND = [
    (r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "official mlpack (vpp_backup)"),
    (r"F:\sr2-cn\mlpack\patch.vpp_pc", "mlpack"),
    (r"F:\sr2-cn\pristine\patch.vpp_pc", "pristine"),
    (r"F:\sr2-cn\_ref92\黑道圣徒2简体汉化补丁\patch.vpp_pc", "ref92 cn patch"),
    (r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc", "INSTALLED"),
]
for p, tag in CAND:
    if not os.path.isfile(p):
        print("(missing) %s  %s" % (tag, p)); continue
    print("=" * 72)
    print("%s\n  %s  size=%d" % (tag, p, os.path.getsize(p)))
    try:
        v = Vpp(p)
    except Exception as ex:
        print("  !!", ex); continue
    hits = [e for e in v.entries()
            if e["name"].lower().startswith("fnt") or "vint_proj" in e["name"].lower()
            or "charlist" in e["name"].lower() or e["name"].lower().startswith("font")]
    for e in sorted(hits, key=lambda e: (e["name"], e["ext"])):
        b = v.read(e)
        extra = ""
        if e["ext"] == "vf3_pc":
            import struct
            extra = " N=%d" % struct.unpack_from("<I", b, 8)[0]
        print("   %-24s ext=%-10s size=%-9d md5=%s%s" % (
            e["name"], e["ext"], e["size"], hashlib.md5(b).hexdigest()[:12], extra))
    if not hits:
        print("   (no fnt/charlist/vint_proj entries)")
