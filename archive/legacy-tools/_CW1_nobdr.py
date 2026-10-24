import os, sys, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from _vpp import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
KEY = ("chinese", "nobdr", "fnt_", "charlist")
for f in os.listdir(G):
    if not f.lower().endswith((".vpp_pc", ".vpp")): continue
    try:
        v = Vpp(os.path.join(G, f)); ents = v.entries()
    except Exception: continue
    for e in ents:
        nm = e["name"].lower()
        if any(k in nm for k in ("chinese", "nobdr")):
            b = v.read(e)
            print("%-16s %-30s size=%-9d md5=%s" % (f, e["name"] + "." + e["ext"], len(b), hashlib.md5(b).hexdigest()[:12]))

print("\n=== pegs.vpp_pc 全部字体 peg 全文 ===")
v = Vpp(os.path.join(G, "pegs.vpp_pc"))
for e in v.entries():
    if e["name"].startswith("fnt_") or e["name"] in ("jap", "ug-debug", "ige_regular", "ige_small", "ige_smallest"):
        b = v.read(e)
        import re
        txt = re.findall(rb"[ -~]{5,}", b)
        dims = ""
        if len(b) > 32:
            w_, h_ = int.from_bytes(b[0x1C:0x1E], "little"), int.from_bytes(b[0x1E:0x20], "little")
            dims = "w=%d h=%d" % (w_, h_)
        print("%-16s %-4d %s  strs=%s" % (e["name"], len(b), dims, [t.decode() for t in txt]))
