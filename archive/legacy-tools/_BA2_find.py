# -*- coding: utf-8 -*-
import sys, struct, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from _vpp import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
gv = Vpp(GAME)
buf = gv.read(gv.find('static_CH'))
magic, ver, buckets, count = struct.unpack_from('<IHHI', buf, 0)
print('magic', hex(magic), 'ver', ver, 'buckets', buckets, 'count', count, 'len', len(buf))

TARGET = [403,1868,91,102,111,114,109,97,116,93,91,99,111,108,111,114,58,103,114,101,101,110,93,1067,454,364,91,47,102,111,114,109,97,116,93,2699,2328,403,1868,423,1222]

def parse(absolute):
    recs = []
    base = 0x0C + buckets * 8
    for b in range(buckets):
        c, off = struct.unpack_from('<II', buf, 0x0C + b * 8)
        p = (off if absolute else base + off)
        for i in range(c):
            if p + 4 > len(buf):
                break
            h = struct.unpack_from('>I', buf, p)[0]
            p += 4
            slots = []
            while p + 2 <= len(buf):
                v = struct.unpack_from('>H', buf, p)[0]
                p += 2
                if v == 0:
                    break
                slots.append(v)
            recs.append((h, slots, p))
    return recs

for absmode in (False, True):
    recs = parse(absmode)
    print(f'--- absolute={absmode}: {len(recs)} records')
    # 找目标槽位串
    hit = [r for r in recs if r[1] == TARGET]
    print('   exact TARGET hits:', len(hit), [hex(h) for h,_,_ in hit])
    # 找前缀 [403,1868,91,102]
    pre = [r for r in recs if r[1][:4] == [403,1868,91,102]]
    print('   prefix [403,1868,91,102] hits:', len(pre))
    for h,s,_ in pre[:5]:
        print('     hash', hex(h), 'len', len(s), s[:12], '...')
    # 找含 1868 的记录
    c1868 = [r for r in recs if 1868 in r[1]]
    print('   records containing slot 1868:', len(c1868))
