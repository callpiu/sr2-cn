import sys, os, shutil, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G  = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()

# ---------- 1) 回退无效的 common.vpp_pc（proj 改动）----------
ccp = os.path.join(G, "common.vpp_pc")
cbak = r"F:\sr2-cn\_backup_C\common.vpp_pc.before_projfont"
if os.path.exists(cbak):
    shutil.copy2(cbak, ccp)
    print("[revert] common.vpp_pc ->", md5(ccp))
else:
    print("[revert] 备份不存在，跳过")

# ---------- 2) 改 patch.vpp_pc 的 hud_msg.lua：去掉 font 覆盖 ----------
pp = os.path.join(G, "patch.vpp_pc")
BK = r"F:\sr2-cn\_backup_P"
os.makedirs(BK, exist_ok=True)
bak = os.path.join(BK, "patch.vpp_pc.before_nofont")
if not os.path.exists(bak):
    shutil.copy2(pp, bak)
    print("[backup] ->", bak)

print("patch.vpp_pc md5 BEFORE:", md5(pp))
v = Vpp(pp)
e = v.find("hud_msg", "lua")
assert e, "hud_msg.lua not found"
raw = bytearray(v.read(e))
OLD = b'vint_set_property(o, "font", "thin_overlay")'
NEW = b'-- font left to engine default (was thin_overlay / N=224 ASCII font)'
assert raw.count(OLD) == 1, "expected exactly one font line, got %d" % raw.count(OLD)
raw = raw.replace(OLD, NEW)
v.replace_body_appended(e, bytes(raw))
v.save(pp)
print("patch.vpp_pc md5 AFTER :", md5(pp))

# 回读校验
v2 = Vpp(pp)
t = v2.read(v2.find("hud_msg", "lua")).decode("utf-8", "replace")
for ln in t.splitlines():
    if "font" in ln:
        print("   NOW:", ln.strip())
print("REVERT:", bak, "->", pp)
