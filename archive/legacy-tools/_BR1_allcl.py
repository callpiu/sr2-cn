# -*- coding: utf-8 -*-
import os, sys, hashlib, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp

TARGETS = []
for p in [
    r"F:\sr2-cn\_backup_F\common.official_20261013_175139.vpp_pc",
    r"F:\sr2-cn\_backup_F\common.patched_20261013_174215_to_be_rolled_back.vpp_pc",
    r"F:\sr2-cn\_patchsrc\patch.vpp_pc",
    r"F:\sr2-cn\_src2\patch.vpp_pc",
    r"F:\sr2-cn\_src2\patch.vpp_pc.原版对照",
    r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc",
    r"G:\SteamLibrary\steamapps\common\Saints Row 2\common.vpp_pc",
    r"G:\SteamLibrary\steamapps\common\Saints Row 2\textures.vpp_pc",
]:
    if os.path.exists(p):
        TARGETS.append(p)

for p in TARGETS:
    print("=" * 90)
    print("VPP:", p, os.path.getsize(p))
    try:
        v = Vpp(p)
    except Exception as ex:
        print("  !! open fail:", ex); continue
    hits = 0
    for e in v.entries():
        n = e['name'].lower()
        if 'charlist' in n:
            b = v.read(e)
            h = hashlib.md5(b).hexdigest()[:10]
            print("  %-28s ext=%-8s size=%-8d md5=%s" % (e['name'], e['ext'], len(b), h))
            hits += 1
    if not hits:
        print("  (no charlist entries)")
