import sys, os, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
KEY = ("chinese", "nobdr", "fnt_", "charlist", "overlay")

def scan(tag, path):
    if not os.path.exists(path):
        print("  MISSING", path)
        return
    v = Vpp(path)
    print("=== %s  (%d bytes) ===" % (tag, os.path.getsize(path)))
    for e in v.entries():
        nm = e["name"].lower()
        if any(k in nm for k in KEY):
            b = v.read(e)
            print("   %-30s .%-12s %9d  md5=%s" % (e["name"], e.get("ext") or "(none)", len(b), hashlib.md5(b).hexdigest()[:12]))

for f in ("patch.vpp_pc", "common.vpp_pc", "textures.vpp_pc"):
    scan("GAME:" + f, os.path.join(G, f))
print()
for f in ("patch.vpp_pc.orig", "textures.vpp_pc.orig", "common.vpp_pc.orig"):
    scan("ORIG:" + f, os.path.join(r"F:\sr2-cn\vpp_backup", f))
