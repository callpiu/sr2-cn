import sys, os, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
print("=== 搜索所有 VPP 中的 fnt_* 条目 ===")
for f in ("patch.vpp_pc","common.vpp_pc","textures.vpp_pc"):
    p = os.path.join(G,f)
    v = Vpp(p)
    for e in v.entries():
        if e["name"].startswith("fnt_"):
            b = v.read(e)
            print("  %-16s %-26s .%-10s %9d  md5=%s" % (f, e["name"], e.get("ext") or "(none)", len(b), hashlib.md5(b).hexdigest()[:10]))
print()
print("=== 官方原版 VPP 中的 fnt_* ===")
for f in ("patch.vpp_pc.orig","textures.vpp_pc.orig"):
    p = os.path.join("F:\sr2-cn\vpp_backup", f)
    if not os.path.exists(p): continue
    v = Vpp(p)
    for e in v.entries():
        if e["name"].startswith("fnt_"):
            b = v.read(e)
            print("  %-22s %-26s .%-10s %9d  md5=%s" % (f, e["name"], e.get("ext") or "(none)", len(b), hashlib.md5(b).hexdigest()[:10]))
