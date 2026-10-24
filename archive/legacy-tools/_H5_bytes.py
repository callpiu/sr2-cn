# -*- coding: utf-8 -*-
"""不猜记录结构，直接分析：
- patch_us vs patch_ch 是否逐字节相同
- juiced_us vs juiced_ch 差异
- 槽位频率统计（u16）
"""
import os, hashlib, struct, collections

S = r'G:\SteamLibrary\steamapps\common\Saints Row 2\Mods\JUICED - Strings'

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

pairs = [
    ('patch_us.le_strings', 'patch_ch.le_strings'),
    ('juiced_US.le_strings', 'juiced_CH.le_strings'),
    ('static_US.le_strings', '../static_US.le_strings'),
]
for a, b in pairs:
    pa = os.path.normpath(os.path.join(S, a))
    pb = os.path.normpath(os.path.join(S, b))
    ea, eb = os.path.exists(pa), os.path.exists(pb)
    print('%-24s %s  %s' % (a, md5(pa) if ea else 'MISSING', 'size=%d' % os.path.getsize(pa) if ea else ''))
    print('%-24s %s  %s' % (os.path.basename(b), md5(pb) if eb else 'MISSING', 'size=%d' % os.path.getsize(pb) if eb else ''))
    if ea and eb:
        print('   SAME' if md5(pa) == md5(pb) else '   DIFF')
    print()

# 槽位频率：只看 patch_ch / juiced_CH / static(Mods)/static_US
for fn, path in [
    ('patch_ch', os.path.join(S, 'patch_ch.le_strings')),
    ('juiced_CH', os.path.join(S, 'juiced_CH.le_strings')),
    ('static_US(Mods)', r'G:\SteamLibrary\steamapps\common\Saints Row 2\Mods\static_US.le_strings'),
]:
    raw = open(path, 'rb').read()
    us = struct.unpack_from('<%dH' % (len(raw) // 2), raw, 0)
    cnt = collections.Counter(us)
    top = cnt.most_common(12)
    print('%-18s len=%d u16count=%d top12=%s' % (fn, len(raw), len(us), top))
