import sys, os, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
want = ("static_CH", "voice_script_CH", "platform_pc_CH", "charlist_CH", "fnt_chinese")
for f in ("patch.vpp_pc", "common.vpp_pc", "textures.vpp_pc"):
    p = os.path.join(G, f)
    if not os.path.exists(p):
        continue
    v = Vpp(p)
    print("=== %s ===" % f)
    for e in v.entries():
        nm = e["name"]
        if any(w in nm for w in want):
            b = v.read(e)
            print("   %-24s .%-12s %8d  md5=%s" % (nm, e.get("ext", ""), len(b), hashlib.md5(b).hexdigest()[:10]))
print()
print("=== Mods loose files ===")
for dp, dns, fns in os.walk(os.path.join(G, "Mods")):
    for fn in sorted(fns):
        low = fn.lower()
        if low.endswith((".le_strings", ".vf3_pc", ".g_peg_pc", ".txt")) or "charlist" in low or "string" in low:
            fp = os.path.join(dp, fn)
            rel = os.path.relpath(fp, G)
            print("   %-58s %8d  md5=%s" % (rel, os.path.getsize(fp), hashlib.md5(open(fp, "rb").read()).hexdigest()[:10]))
