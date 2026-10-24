"""FT3: inspect the reference Chinese patch to see how a working patch handles
the fonts + charlist.
"""
import sys, os, struct, hashlib, glob
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

REF = r"F:\sr2-cn\_ref92"
print("ref tree:")
for root, dirs, files in os.walk(REF):
    for f in files:
        fp = os.path.join(root, f)
        print("   %-70s %d" % (os.path.relpath(fp, REF), os.path.getsize(fp)))

for p in glob.glob(os.path.join(REF, "**", "*.vpp_pc"), recursive=True):
    print("=" * 70)
    print(p, os.path.getsize(p))
    v = Vpp(p)
    for e in v.entries():
        if e["name"].lower().startswith("fnt") or "charlist" in e["name"].lower() or e["ext"] in ("vf3_pc",):
            b = v.read(e)
            extra = ""
            if e["ext"] == "vf3_pc":
                extra = " N=%d" % struct.unpack_from("<I", b, 8)[0]
            if e["ext"] == "txt" and "charlist" in e["name"]:
                import re
                m = re.search(rb"count=(\d+)", b)
                extra = " count=%s" % (m.group(1).decode() if m else "?")
            print("   %-24s ext=%-10s size=%-9d md5=%s%s" % (
                e["name"], e["ext"], e["size"], hashlib.md5(b).hexdigest()[:12], extra))
