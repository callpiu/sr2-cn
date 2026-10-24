# -*- coding: utf-8 -*-
"""Restore game patch.vpp_pc charlist_CH to the author's original (2795 items)."""
import sys, struct, io, os, shutil, hashlib, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

GAME_PATCH = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"
AUTHOR = r"F:\sr2-cn\_patchsrc\patch.vpp_pc"
BK = r"F:\sr2-cn\_backup_K"
os.makedirs(BK, exist_ok=True)

gp = Vpp(GAME_PATCH)
ap = Vpp(AUTHOR)
e_g = gp.find("charlist_CH", "txt")
e_a = ap.find("charlist_CH", "txt")
dg = gp.read(e_g)
da = ap.read(e_a)
print("game charlist size=%d md5=%s" % (len(dg), hashlib.md5(dg).hexdigest()[:12]))
print("author charlist size=%d md5=%s" % (len(da), hashlib.md5(da).hexdigest()[:12]))
if dg == da:
    print("already identical, nothing to do")
    sys.exit(0)

bak = os.path.join(BK, "patch.before_charlist_restore_%s.vpp_pc" % time.strftime("%Y%m%d_%H%M%S"))
print("backing up game patch.vpp_pc ->", bak)
shutil.copy2(GAME_PATCH, bak)
print("backup size", os.path.getsize(bak))

gp.replace_body_appended(e_g, da)
gp.save(GAME_PATCH)
print("saved. new size", os.path.getsize(GAME_PATCH))

# verify
v2 = Vpp(GAME_PATCH)
d2 = v2.read(v2.find("charlist_CH", "txt"))
print("verify md5=%s  match_author=%s" % (hashlib.md5(d2).hexdigest()[:12], d2 == da))
