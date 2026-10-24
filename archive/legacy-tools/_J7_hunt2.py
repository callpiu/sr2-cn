# -*- coding: utf-8 -*-
"""放宽搜索：大端/小端 + 单个 unit 值定位。"""
import sys, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(G + '/patch.vpp_pc')

WANT = [371, 1836, 1035, 422, 332, 2667, 2296, 391, 1190]
GOT = [336, 1784, 410, 967, 362, 2656, 2268, 354, 2342]
SUB1 = WANT[:3]   # 你的弟
SUB2 = GOT[:3]

def seq(units, endian):
    b = bytearray()
    for u in units:
        b += struct.pack(('>' if endian == 'be' else '<') + 'H', u)
    return bytes(b)

for nm in ['static_CH', 'voice_script_CH', 'platform_pc_CH']:
    try:
        raw = v.read(v.find(nm, 'le_strings'))
    except Exception as e:
        print(nm, 'ERR', e)
        continue
    print('=== %s size=%d ===' % (nm, len(raw)))
    for endian in ('le', 'be'):
        for tag, us in [('WANT3', SUB1), ('GOT3', SUB2)]:
            p = seq(us, endian)
            hits = []
            i = raw.find(p)
            while i >= 0 and len(hits) < 5:
                hits.append(i)
                i = raw.find(p, i + 1)
            if hits:
                print('   %s %s %s -> %s' % (endian, tag, us[:3], hits))
    # 单值 371 / 336 出现位置
    for val in (371, 336):
        p = struct.pack('<H', val)
        cnt = raw.count(p)
        print('   unit=%d(<u16) 出现 %d 次' % (val, cnt))
