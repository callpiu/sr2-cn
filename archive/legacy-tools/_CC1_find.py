# -*- coding: utf-8 -*-
"""在所有 le_strings 里搜字幕文本，比较 slots"""
import struct, sys, os
sys.path.insert(0, r'F:\sr2-cn')
from _vpp import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'

def parse_charlist_bytes(b):
    txt = b.decode('latin1'); codes = []
    for line in txt.replace('\r\n', '\n').split('\n'):
        line = line.strip()
        if not line or line.startswith('/') or line.startswith('count='):
            continue
        codes.append(int(line))
    return codes

def build(codes):
    c2u, u2c, nxt = {}, {}, 0x100
    for u in codes:
        if u < 256:
            c2u[u] = u; u2c[u] = u
        else:
            c2u[nxt] = u; u2c[u] = nxt; nxt += 1
    return c2u, u2c

def parse_lestrings(data):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', data, 0)
    if magic != 0xA84C7F73:
        return None
    recs = []
    for b in range(buckets):
        o = 0x0C + b * 8
        bc, boff = struct.unpack_from('<II', data, o)
        if bc == 0 or boff + bc * 4 > len(data):
            continue
        for k in range(bc):
            roff = struct.unpack_from('<I', data, boff + k * 4)[0]
            if roff + 6 > len(data):
                continue
            h = struct.unpack_from('>I', data, roff)[0]
            slots, p = [], roff + 4
            while p + 2 <= len(data):
                val = struct.unpack_from('>H', data, p)[0]; p += 2
                if val == 0: break
                slots.append(val)
            recs.append((h, slots, roff))
    return recs

v = Vpp(os.path.join(GAME, 'patch.vpp_pc'))
cl = None
for e in v.entries():
    if e['name'].lower() == 'charlist_ch':
        cl = v.read(e)
codes = parse_charlist_bytes(cl)
c2u, u2c = build(codes)

KEYS = ('弟兄', '保护', '需要', '出去谈', '生意')

for e in v.entries():
    if e['ext'].lower() != 'le_strings':
        continue
    if 'CH' not in e['name']:
        continue
    data = v.read(e)
    recs = parse_lestrings(data)
    if recs is None:
        continue
    hits = []
    for h, slots, roff in recs:
        t = ''.join(chr(c2u[s]) if s in c2u else '' for s in slots)
        for k in KEYS:
            if k in t:
                hits.append((h, slots, t)); break
    print("=== %-22s recs=%-6d hits=%d" % (e['name'], len(recs), len(hits)))
    for h, slots, t in hits[:12]:
        print("     hash=%08X  slots=%s" % (h, slots[:26]))
        print("        -> %r" % t)
