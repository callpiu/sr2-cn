# -*- coding: utf-8 -*-
"""扫描所有 VPP（含原版备份）中的 charlist_CH / fnt_chinese"""
import sys, os, glob, hashlib
sys.path.insert(0, r'F:\sr2-cn')
from _vpp import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
TARGETS = {'charlist_ch', 'fnt_chinese'}

paths = []
for pat in (os.path.join(GAME, '*.vpp_pc'),
            r'F:\sr2-cn\vpp_backup\*.vpp_pc*',
            os.path.join(GAME, 'DLC', '*.vpp_pc'),
            os.path.join(GAME, 'data', '*.vpp_pc')):
    paths += glob.glob(pat)
paths += glob.glob(os.path.join(GAME, '**', '*.vpp_pc'), recursive=False)

seen = set()
for p in paths:
    if p in seen or not os.path.isfile(p):
        continue
    seen.add(p)
    try:
        v = Vpp(p)
    except Exception:
        continue
    hits = []
    for e in v.entries():
        n = e['name'].lower()
        if n in TARGETS:
            body = v.read(e)
            hits.append((e['name'], e['size'], hashlib.md5(body).hexdigest()[:12]))
    if hits:
        print("%-58s %s" % (os.path.relpath(p, GAME), ''))
        for n, s, m in hits:
            print("      %-18s size=%-9d md5=%s" % (n, s, m))
