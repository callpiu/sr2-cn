# -*- coding: utf-8 -*-
"""列出各 VPP 内 fnt_* / charlist_* 条目"""
import sys, os, hashlib
sys.path.insert(0, r'F:\sr2-cn')
from _vpp import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'

for name in ('common.vpp_pc', 'patch.vpp_pc', 'textures.vpp_pc', 'pegs.vpp_pc',
             'interface.vpp_pc', 'misc.vpp_pc'):
    p = os.path.join(GAME, name)
    if not os.path.exists(p):
        continue
    try:
        v = Vpp(p)
    except Exception as e:
        print("!! %s : %s" % (name, e))
        continue
    hits = []
    for e in v.entries():
        n = e["name"].lower()
        if n.startswith('fnt_') or n.startswith('charlist') or 'chinese' in n:
            hits.append(e)
    if hits:
        print("=== %s (%d entries, %d hits) ===" % (name, len(v.entries()), len(hits)))
        for e in hits:
            body = v.read(e)
            print("   %-40s size=%-9d md5=%s" % (e["name"], len(body), hashlib.md5(body).hexdigest()[:12]))
