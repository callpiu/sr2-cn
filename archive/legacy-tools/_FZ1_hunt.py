"""FZ1: hunt for every charlist-like file in the game install."""
import sys, os, struct, glob
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, MAGIC_VPP

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

vpps = sorted(glob.glob(os.path.join(G, "*.vpp_pc")))
print("VPPs:", len(vpps))
for p in vpps:
    try:
        v = Vpp(p)
        ents = v.entries()
    except Exception as ex:
        print("  !! %s : %s" % (os.path.basename(p), ex))
        continue
    hit = [e for e in ents if "charlist" in e["name"].lower()]
    if hit:
        print("== %s (%d entries)" % (os.path.basename(p), len(ents)))
        for e in hit:
            print("     %-28s ext=%-10s size=%d" % (e["name"], e["ext"], e["size"]))

print()
# loose files anywhere in the tree
print("loose charlist* on disk:")
for root, dirs, files in os.walk(G):
    for f in files:
        if "charlist" in f.lower():
            fp = os.path.join(root, f)
            print("   %s  (%d bytes)" % (os.path.relpath(fp, G), os.path.getsize(fp)))
