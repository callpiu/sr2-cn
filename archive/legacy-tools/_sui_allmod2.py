import re, os, sys, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
MODS = G + 'Mods/'
v = Vpp(G + 'patch.vpp_pc')

# 收集 Mods lua 里所有 tag
all_tags = {}
for fn in os.listdir(MODS):
    if not fn.endswith('.lua'):
        continue
    txt = open(MODS + fn, 'rb').read().decode('latin1')
    for m in re.finditer(r'"([A-Z][A-Z0-9_]{3,60})"', txt):
        all_tags.setdefault(m.group(1), set()).add(fn)

sui = sorted(t for t in all_tags if t.startswith('SUI_'))

def U16(s):
    return s.encode('utf-16-be')

# 1) CH 表里是否存在（tag 名本身不在表里，tag 名只在 lua；表里存的是 hash）
#    => 无法用名字查。但可以反向：官方 lua（VPP 内）里的 tag 是官方的，
#       Mods 里出现但 VPP 官方 lua 里没有的 => mod 自造。
official = set()
for e in v.entries():
    if e['ext'] != 'lua':
        continue
    try:
        txt = v.read(e).decode('latin1')
    except Exception:
        continue
    for m in re.finditer(r'"([A-Z][A-Z0-9_]{3,60})"', txt):
        official.add(m.group(1))

print('官方 lua tag 总数:', len(official))
print()
print('=== SUI_ tag 判定：官方是否存在 ===')
missing = []
for t in sui:
    in_off = t in official
    mark = '官方有' if in_off else '★ 自造(表里查不到)'
    print('   %-40s %-18s  lua: %s' % (t, mark, sorted(all_tags[t])[:2]))
    if not in_off:
        missing.append(t)

print()
print('mod 自造 tag 数量:', len(missing))

# 2) 用另一种方法交叉验证：静态搜 patch.vpp_pc 里这些 tag 名是否作为 ASCII 出现
#    （XTBL 里的 Identifier 就是纯 ASCII tag 名，可直接搜）
print()
print('=== 在 patch.vpp_pc 全文搜这些 tag（XTBL Identifier 用 ASCII） ===')
buf = open(G + 'patch.vpp_pc', 'rb').read()
for t in sui:
    a = buf.count(t.encode())
    b = buf.count(U16(t))
    print('   %-40s ascii=%d utf16be=%d' % (t, a, b))