"""FR3: list every fnt_* entry in patch / textures / common / pegs, and check the
font payload set that `fnt_chinese` needs.
"""
import sys, os, glob, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

for name in ("patch.vpp_pc", "textures.vpp_pc", "common.vpp_pc", "pegs.vpp_pc"):
    p = os.path.join(G, name)
    if not os.path.isfile(p):
        print("(missing)", name); continue
    v = Vpp(p)
    ents = [e for e in v.entries() if e["name"].lower().startswith("fnt") or "chinese" in e["name"].lower()]
    print("=" * 70)
    print("%s  (%d entries)" % (name, len(v.entries())))
    for e in sorted(ents, key=lambda e: e["name"]):
        md5 = hashlib.md5(v.read(e)).hexdigest()[:12]
        print("   %-28s ext=%-10s size=%-9d md5=%s" % (e["name"], e["ext"], e["size"], md5))

print()
print("== any entry whose name contains 'chinese' anywhere ==")
for p in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    v = Vpp(p)
    for e in v.entries():
        if "chinese" in e["name"].lower() or "nobdr" in e["name"].lower():
            print("   %-16s %-28s ext=%s size=%d" % (os.path.basename(p), e["name"], e["ext"], e["size"]))
