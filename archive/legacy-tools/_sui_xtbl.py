import re, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')

print('=== patch 内 xtbl 条目 ===')
for e in v.entries():
    if 'xtbl' in e['name'].lower() or e['ext'].lower() in ('xtbl',):
        print('  %-40s size=%d' % (e['name'] + '.' + e['ext'], e['size']))

print()
print('=== patch 内所有条目里搜 SUI_LAN / SUI_ / COOP_LOAD_EXPLANATION ===')
probes = [b'SUI_LAN', b'SUI_', b'COOP_LOAD_EXPLANATION_TEXT', b'COOP_TITLE', b'COOP_WAIT']
for e in v.entries():
    try:
        data = v.read(e)
    except Exception:
        continue
    for pr in probes:
        c = data.count(pr)
        if c:
            print('  %-44s %s x%d' % (e['name'] + '.' + e['ext'], pr.decode(), c))

print()
print('=== common.vpp_pc 搜同样的 tag ===')
import os
for V in ['common.vpp_pc', 'city_load.vpp_pc', 'textures.vpp_pc']:
    p = G + V
    if not os.path.exists(p):
        continue
    b = open(p, 'rb').read()
    print(' %s size=%d' % (V, len(b)))
    for pr in probes:
        c = b.count(pr)
        if c:
            i = 0
            while True:
                i = b.find(pr, i)
                if i < 0:
                    break
                print('    %s @%08X  ctx=%r' % (pr.decode(), i, b[max(0, i - 60):i + 80]))
                i += len(pr)
                break
            print('    %s total %d' % (pr.decode(), c))