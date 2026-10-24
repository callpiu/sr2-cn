# -*- coding: utf-8 -*-
"""在各 le_strings（VPP 内 + Mods 散装）中搜索 unit 序列：
期望(你=371,的=1836,弟=1035,兄=422,们=332,需=2667,要=2296,保=391,护=1190)
实际(336,1784,410,967,362,2656,2268,354,2342)
在文件中按 u16 找连续片段。
"""
import sys, struct, os
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'

def u16seq(units):
    b = bytearray()
    for u in units:
        b += bytes(((u >> 8) & 0xFF, u & 0xFF))
    return bytes(b)

WANT = [371, 1836, 1035, 422, 332, 2667, 2296, 391, 1190]
GOT = [336, 1784, 410, 967, 362, 2656, 2268, 354, 2342]

targets = {}
targets['want'] = u16seq(WANT)
targets['got'] = u16seq(GOT)

v = Vpp(G + '/patch.vpp_pc')
names = [(e['name'], e['ext']) for e in v.entries() if e['name'].endswith('_CH') or 'ch' in e['ext'].lower()]
print('patch.vpp_pc 中文相关:', [n for n in names if n[0].endswith('CH')])

for nm, ext in names:
    if not nm.endswith('_CH'):
        continue
    try:
        raw = v.read(v.find(nm, ext))
    except Exception:
        continue
    for tag, pat in targets.items():
        i = raw.find(pat)
        if i >= 0:
            print('  %s.%s: %s 命中 @%d' % (nm, ext, tag, i))
    # 部分匹配（前3个unit）
    for tag, pat in targets.items():
        i = raw.find(pat[:6])
        if i >= 0:
            print('  %s.%s: %s 部分命中 @%d' % (nm, ext, tag, i))
