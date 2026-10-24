import re, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')

names = ['multi_pause_menu', 'menu_base', 'pause_menu', 'main_menu',
         'coop_test', 'hud_coop_div', 'mp_hud', 'dialog_box']

for nm in names:
    try:
        e = v.find(nm, 'lua')
    except Exception:
        e = None
        for x in v.entries():
            if x['name'] == nm:
                e = x
                break
    if e is None:
        print(nm, 'NOT FOUND')
        continue
    txt = v.read(e).decode('latin1')
    hits = [kw for kw in ['SUI', 'COOP_', '_SP', 'LAN'] if kw in txt]
    print('=== %s  size=%d  hits=%s' % (nm, e['size'], hits))
    for kw in hits:
        for m in re.finditer(re.escape(kw), txt):
            a = max(0, m.start() - 200)
            b = min(len(txt), m.end() + 200)
            print('   [%s] ...%s...' % (kw, txt[a:b].replace('\n', ' ')))
            break
    print()