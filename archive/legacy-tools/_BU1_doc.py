# -*- coding: utf-8 -*-
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp
GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(GAME, 'common.vpp_pc'))
for e in v.entries():
    if e['name'].lower() in ('hud', 'hud_gsi', 'activity_level') and e['ext'] in ('vint_doc', 'vint_xdoc'):
        b = v.read(e)
        t = b.decode('utf-8', 'replace')
        print("=== %s.%s  size=%d ===" % (e['name'], e['ext'], len(b)))
        fonts = re.findall(r'font[^,;\n<>]{0,60}', t, re.I)
        from collections import Counter
        c = Counter(fonts)
        for k, n in c.most_common(30):
            print("   %4d  %s" % (n, k.strip()[:90]))
        print()
