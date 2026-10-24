# -*- coding: utf-8 -*-
"""列出各 VPP 内 le_strings / charlist 条目；导出 charlist_CH"""
import sys, os, hashlib
sys.path.insert(0, r'F:\sr2-cn')
from _vpp import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
OUT = r'F:\sr2-cn\_fontdump'

for name in ('patch.vpp_pc', 'common.vpp_pc'):
    v = Vpp(os.path.join(GAME, name))
    print("=== %s ===" % name)
    for e in v.entries():
        n = e['name'].lower()
        x = e['ext'].lower()
        if 'string' in n or 'le_' in n or x in ('le_strings', 'strings') or 'local' in n:
            print("   %-45s .%-12s size=%-9d" % (e['name'], e['ext'], e['size']))

# 导出 charlist_CH
v = Vpp(os.path.join(GAME, 'patch.vpp_pc'))
for e in v.entries():
    if e['name'].lower() == 'charlist_ch':
        body = v.read(e)
        open(os.path.join(OUT, 'charlist_CH.txt'), 'wb').write(body)
        print("\ncharlist_CH exported: %d bytes md5=%s" % (len(body), hashlib.md5(body).hexdigest()[:12]))
        break
