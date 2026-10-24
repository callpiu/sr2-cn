# -*- coding: utf-8 -*-
"""正确解析 XTBL 格式的 MultiMenu_text / MultiTemp_text，找 OpenSpy 相关条目"""
import struct, sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')

def dump_xtbl(name, ext=''):
    try:
        blob = v.read(v.find(name, ext))
    except Exception as e:
        print('%s: 读取失败 %s' % (name, e))
        return
    print('=== %s (%d B) ===' % (name, len(blob)))
    # 1) null 分隔
    parts = blob.split(b'\x00')
    hits = [p for p in parts if p and (b'OpenSpy' in p or b'GameSpy' in p)]
    if hits:
        print('  [null分隔] 命中 %d' % len(hits))
        for h in hits:
            print('    %r' % h)
    # 2) ASCII 扫
    n = blob.count(b'OpenSpy')
    print('  ASCII "OpenSpy" x%d' % n)
    if n:
        i = 0
        while True:
            i = blob.find(b'OpenSpy', i)
            if i < 0: break
            print('    @%08X ctx=%r' % (i, blob[max(0, i - 70):i + 90]))
            i += 1
    # 3) UTF-8 扫
    n = blob.count('OpenSpy'.encode('utf-8'))
    if n:
        print('  UTF-8 "OpenSpy" x%d' % n)
    print()

for nm in ['MultiMenu_text', 'MultiTemp_text', 'MultiTemp', 'MultiStats',
           'MultiGames_text', 'PC_text', 'Menus_text', 'Item_text']:
    dump_xtbl(nm)