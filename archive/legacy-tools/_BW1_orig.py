# -*- coding: utf-8 -*-
import os, sys, hashlib, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp

def show(path, tag):
    print("=" * 80)
    print(tag, path, os.path.getsize(path))
    v = Vpp(path)
    for e in v.entries():
        n = e['name'].lower()
        if 'fnt' in n or 'charlist' in n or 'font' in n:
            b = v.read(e)
            print("   %-34s %-10s %-9d md5=%s" % (e['name'], e['ext'], len(b), hashlib.md5(b).hexdigest()[:10]))

show(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "原版 patch")
show(r"F:\sr2-cn\vpp_backup\textures.vpp_pc.orig", "原版 textures")
