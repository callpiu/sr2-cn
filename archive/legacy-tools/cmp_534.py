import os, sys, hashlib, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
files = {
 "v534_当前(48.7M)": "patch.vpp_pc",
 "v534前(49.1M)":    "patch.vpp_pc.v20261012_144927_before_v534.bak",
 "144927前(49.1M)":  "patch.vpp_pc.v20261012_143820_before_ammo.bak",
 "v532(48.7M)":      "patch.vpp_pc.v532_before_exp.bak",
}
print("=== 各版本的关键条目 ===")
for lab, fn in files.items():
    p = os.path.join(G, fn)
    if not os.path.exists(p): continue
    v = Vpp(p)
    d = {e["name"]+"."+(e["ext"] or ""): e for e in v.entries()}
    def g(k):
        e = d.get(k)
        if not e: return "-"
        b = bytes(v.read(e))
        return "%d/%s" % (e["size"], hashlib.md5(b).hexdigest()[:8].upper())
    print("%-18s %d 条目 %d 字节" % (lab, v.num, os.path.getsize(p)))
    for k in ("charlist_CH.txt","fnt_chinese.vf3_pc","fnt_chinese.g_peg_pc","static_CH.le_strings"):
        print("    %-24s %s" % (k, g(k)))
    print()
