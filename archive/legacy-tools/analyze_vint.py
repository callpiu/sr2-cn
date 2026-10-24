# -*- coding: utf-8 -*-
"""
解析并对比 city_load.vint_doc 与 dialog_box.vint_doc 的字符串表结构，
定位 loading_grp 的属性列表该在哪插入 'thin'。
"""
import sys, re, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'common.vpp_pc')

for nm in ['city_load', 'dialog_box']:
    d = v.read(v.find(nm, 'vint_doc'))
    print('=== %s (%d B) ===' % (nm, len(d)))
    # 找出所有字符串及其偏移
    offs = [(m.start(), m.group().decode()) for m in re.finditer(rb'[ -~]{2,}', d)]
    # 只打印关键区域
    keys = ['loading_grp', 'loading_text', 'dialog_grp', 'body', 'thin', 'header_n']
    for o, s in offs:
        if s in keys or 'grp' in s.lower():
            print('   @%04X %r' % (o, s))
    print()

print()
print('=== city_load.vint_doc 从 loading_grp 开始的原始字节 ===')
d = v.read(v.find('city_load', 'vint_doc'))
i = d.find(b'loading_grp')
print('loading_grp @%d' % i)
print(repr(d[i - 40:]))
open('F:/sr2-cn/_city_load.vint', 'wb').write(d)