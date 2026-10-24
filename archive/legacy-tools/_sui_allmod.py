import re, os, sys, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
MODS = G + 'Mods/'

# 收集 CH 表里所有存在的 tag（按 ID 无法反推 tag 名，但可反推"ID→中文"）
# 反过来做：找出 lua 里所有 tag 字面量，看哪些在 CH 表的 ID 空间里找不到
# 但我们无法从 tag 名算 hash。=> 换策略：直接列出所有 tag，人工/规则筛可疑的。

all_tags = {}
for fn in os.listdir(MODS):
    if not fn.endswith('.lua'):
        continue
    txt = open(MODS + fn, 'rb').read().decode('latin1')
    for m in re.finditer(r'"([A-Z][A-Z0-9_]{3,60})"', txt):
        all_tags.setdefault(m.group(1), set()).add(fn)

print('Mods lua 里 tag 字面量总数:', len(all_tags))

# Juice/mod 自造 tag 的特征：含 SUI_ / SUI_MOD_ / _JUICED_ / 后缀 _JUICED
SUSPECT_PREFIX = ('SUI_', 'SUI_MOD_')
print()
print('=== 含 SUI_ 前缀的 tag（高度可疑：mod 自造）===')
for t in sorted(all_tags):
    if t.startswith('SUI_'):
        print('   %-40s %s' % (t, sorted(all_tags[t])[:3]))

print()
print('=== 含 JUICE / MOD 字样的 tag ===')
for t in sorted(all_tags):
    if 'JUICE' in t or t.startswith('MOD_') or '_MOD_' in t or 'GOTR' in t:
        print('   %-40s %s' % (t, sorted(all_tags[t])[:3]))