# -*- coding: utf-8 -*-
"""穷举记录头布局，对偏移 57280 尝试各种解析，看哪种能得到可读中文。"""
import sys, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp
from sr2strings import CharList

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(G + '/patch.vpp_pc')
raw = v.read(v.find('static_CH', 'le_strings'))
txt = v.read(v.find('charlist_CH', 'txt')).decode()
ns = [int(t) for t in txt.split() if t.lstrip('-').isdigit()]
if ns and ns[0] == len(ns) - 1:
    ns = ns[1:]
CL = CharList(ns)
N = len(raw)

def dec(base, L, endian):
    out = []
    for k in range(L):
        o = base + k * 2
        if o + 1 >= N:
            return None
        u = struct.unpack_from(('>' if endian == 'be' else '<') + 'H', raw, o)[0]
        if u < 0x100:
            out.append(chr(u))
        elif u < len(CL.body):
            out.append(chr(CL.body[u]))
        else:
            out.append('<?%d>' % u)
    return ''.join(out)

for off in (57280, 57302):
    print('=' * 60)
    print('off=%d  head=%s' % (off, raw[off:off + 24].hex()))
    for hlen in (4, 6, 8):
        for lfield in ('u16', 'u32'):
            try:
                if lfield == 'u16':
                    L = struct.unpack_from('<H', raw, off + hlen)[0]
                else:
                    L = struct.unpack_from('<I', raw, off + hlen)[0]
            except Exception:
                continue
            for unitoff in (hlen + (2 if lfield == 'u16' else 4), hlen):
                if not (0 < L < 3000):
                    continue
                for endian in ('le', 'be'):
                    s = dec(off + unitoff, L, endian)
                    if s and any('\u4e00' <= c <= '\u9fff' for c in s):
                        print('  h=%d L=%s=%d unitoff=+%d %s -> %r' % (hlen, lfield, L, unitoff, endian, s[:60]))
