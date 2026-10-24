import re, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')

print('=== patch 内所有 .lua 条目 ===')
luas = []
for e in v.entries():
    if e['ext'] in ('lua', 'LUA') or e['name'].endswith('.lua'):
        luas.append(e)
for e in luas:
    print('  %-46s size=%d' % (e['name'], e['size']))
print('total lua entries', len(luas))

print()
print('=== 在所有 lua 里搜 SUI_ / COOP_ / _SP ===')
for e in luas:
    try:
        data = v.read(e)
    except Exception as ex:
        print('  read fail', e['name'], ex)
        continue
    txt = data.decode('latin1')
    for kw in ['SUI_', 'COOP_', '_SP', 'SUI_LAN']:
        if kw in txt:
            print('  %-40s has %s x%d' % (e['name'], kw, txt.count(kw)))
            for m in re.finditer(re.escape(kw), txt):
                a = max(0, m.start() - 160)
                b = min(len(txt), m.end() + 160)
                print('     ...%s...' % txt[a:b].replace('\n', ' | '))
                break