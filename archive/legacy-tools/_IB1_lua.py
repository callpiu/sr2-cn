# -*- coding: utf-8 -*-
import os, sys, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
luas = [e for e in v.entries() if e['ext'].lower()=='lua']
print("lua 数量:", len(luas))
for e in luas:
    d = v.read(e)
    try: t = d.decode('latin1')
    except: continue
    if re.search(r'subtitle|set_font|"font"|font\s*=', t, re.I):
        hits = [l.strip() for l in t.splitlines() if re.search(r'subtitle|font', l, re.I)]
        print("\n### %s (%d B)" % (e['name'], e['size']))
        for l in hits[:14]:
            print("    ", l[:120])
