# -*- coding: utf-8 -*-
"""验证 delta=32 假说：CH 的 unit - 32 == 正确 charlist 索引。
用 US 文本作为语义参考，推 CH 中文，检查 unit-32 是否给出合理字。
"""
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
CL = CharList(ns)
BODY = CL.body


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


CH = recs(v.read(v.find('static_CH', 'le_strings')))
US = recs(open(G + '/Mods/static_US.le_strings', 'rb').read())

def us_dec(units):
    return ''.join(chr(u) if u < 0x100 else '?' for u in units)

def ch_dec(units, delta):
    out = []
    for u in units:
        if u < 0x100:
            out.append(chr(u))
        else:
            i = u - delta
            out.append(chr(BODY[i]) if 0 <= i < len(BODY) else '{%d}' % u)
    return ''.join(out)

# 用已知样本校准 delta
samples = [0xFE69, 0xEC9A, 0x86C2, 0x6C76, 0x805D]
for hl in [(0, 'no-delta'), (32, 'delta32'), (0x20, 'delta32')]:
    print('==== delta=%s ====' % hl[1])
    for h in samples:
        if h in CH:
            print('  h=%04X US=%-38r CH=%r' % (h, us_dec(US.get(h, []))[:38], ch_dec(CH[h], hl[0])[:40]))
    break

print()
for delta in (0, 32):
    print('delta=%d 样本:' % delta)
    for h in samples:
        if h in CH:
            print('   %04X -> %s' % (h, ch_dec(CH[h], delta)[:40]))
