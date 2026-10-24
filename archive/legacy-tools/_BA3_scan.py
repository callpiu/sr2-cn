# -*- coding: utf-8 -*-
import sys, struct
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from _vpp import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
gv = Vpp(GAME)

def parse(buf):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', buf, 0)
    if magic != 0xA84C7F73:
        return None
    recs = {}
    base = 0x0C + buckets * 8
    for b in range(buckets):
        c, off = struct.unpack_from('<II', buf, 0x0C + b * 8)
        p = base + off
        for i in range(c):
            h = struct.unpack_from('>I', buf, p)[0]; p += 4
            slots = []
            while True:
                v = struct.unpack_from('>H', buf, p)[0]; p += 2
                if v == 0: break
                slots.append(v)
            recs[h] = slots
    return recs

# 特征串: [format] = 91,102,111,114,109,97,116,93 ; 弟兄们 = 1067,454,364
FMT = [91,102,111,114,109,97,116,93]
BRO = [1067,454,364]
H = 0xF284ED87

for e in gv.entries():
    if not e['name'].lower().endswith('.le_strings') and 'static' not in e['name'].lower():
        continue
    try:
        buf = gv.read(e)
    except Exception:
        continue
    r = parse(buf)
    if not r:
        continue
    hasH = H in r
    # 找含 [format] 的记录
    nfmt = 0; nbro = 0; samples = []
    for h, s in r.items():
        st = ''.join(map(str, s))
        if '[format]' and '106,111,114,109,97,116,93' in st:
            nfmt += 1
        # 子串匹配 BRO
        for i in range(len(s)-2):
            if s[i:i+3] == BRO:
                nbro += 1
                if len(samples) < 3:
                    samples.append((hex(h), s))
                break
    print(f"{e['name']}: recs={len(r)} hasF284ED87={hasH} with[format]={nfmt} with弟兄们={nbro}")
    for hx, s in samples:
        print('    ', hx, s)
    if hasH:
        print('    >>> F284ED87 =', r[H])
