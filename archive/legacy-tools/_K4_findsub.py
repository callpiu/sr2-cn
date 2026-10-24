# -*- coding: utf-8 -*-
"""用 delta=32 全量解码 static_CH / voice_script_CH / platform_pc_CH，搜索直升机突击字幕。"""
import sys, struct, os
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp
from sr2strings import CharList

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(G + '/patch.vpp_pc')
txt = v.read(v.find('charlist_CH', 'txt')).decode()
ns = [int(t) for t in txt.split() if t.lstrip('-').isdigit()]
if ns and ns[0] == len(ns) - 1:
    ns = ns[1:]
BODY = CharList(ns).body

def recs(raw):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', raw, 0)
    oa = 16 + buckets * 8
    d = {}
    for i in range(count):
        o = struct.unpack_from('<I', raw, oa + i * 4)[0]
        if not (0 <= o < len(raw) - 4):
            continue
        h = struct.unpack_from('<H', raw, o)[0]
        p = o + 4
        us = []
        while p + 1 < len(raw):
            u = struct.unpack_from('>H', raw, p)[0]
            p += 2
            if u == 0:
                break
            us.append(u)
        d.setdefault(h, us)
    return d

def ch_dec(units, delta=32):
    out = []
    for u in units:
        if u < 0x100:
            out.append(chr(u))
        else:
            i = u - delta
            out.append(chr(BODY[i]) if 0 <= i < len(BODY) else '{%d}' % u)
    return ''.join(out)

KEYS = ['直升机', '突击', '弟兄们', '保护', '面包车', '停靠', '生意', '迷雾巷', '你的', '免遭', '袭击']
for nm, ext in [('static_CH', 'le_strings'), ('voice_script_CH', 'le_strings'), ('platform_pc_CH', 'le_strings')]:
    D = recs(v.read(v.find(nm, ext)))
    print('=== %s  记录=%d ===' % (nm, len(D)))
    n = 0
    for h, us in D.items():
        s = ch_dec(us)
        if any(k in s for k in KEYS):
            print('   h=%04X  %s' % (h, s[:100]))
            n += 1
            if n > 30:
                break
    print('   命中 %d' % n)
