import re, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')

# 收集所有 lua 里的 string literal tag
tags = {}
for e in v.entries():
    if e['ext'] != 'lua':
        continue
    try:
        txt = v.read(e).decode('latin1')
    except Exception:
        continue
    for m in re.finditer(r'"([A-Z][A-Z0-9_]{4,60})"', txt):
        t = m.group(1)
        tags.setdefault(t, set()).add(e['name'])

print('lua 里出现的 tag 字面量总数:', len(tags))
print()
print('=== 含 SP / SINGLE / COOP / MODE 的 tag ===')
for t in sorted(tags):
    if any(k in t for k in ['_SP', 'SINGLE', 'COOP', 'MODE_5', 'LAN']):
        print('   %-40s %s' % (t, sorted(tags[t])[:3]))

print()
print('=== 精确找 SINGLE 相关 ===')
for t in sorted(tags):
    if 'SINGLE' in t.upper():
        print('   ', t)

print()
print('=== 含 MODE_5 的 ===')
for t in sorted(tags):
    if 'MODE_5' in t:
        print('   ', t, sorted(tags[t])[:3])