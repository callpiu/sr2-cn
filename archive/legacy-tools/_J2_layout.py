# -*- coding: utf-8 -*-
"""VPP 内 static_CH 记录布局探测。
已知 off=57280: 76 6c bc 00 | 04 29 | 06 da 09 28 05 72 02 f5 03 ec 02 97 02 2a | 00 00
设 hash=0xB56C? 或 0x00BC6C76。
尝试：hash(4) + u16 L + L*u16 units + 0x0000
"""
import sys, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp
from sr2strings import CharList

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(G + '/patch.vpp_pc')
raw = v.read(v.find('static_CH', 'le_strings'))
txt = v.read(v.find('charlist_CH', 'txt')).decode()
ns = [int(t) for t in txt.split() if t.lstrip('-').isdigit()]
CL = CharList(ns)

def try_layout(off):
    print('--- off=%d ---' % off)
    for desc, hlen in [('hash4+L2', 4), ('hash8+L4', 8), ('hash4+L4', 4)]:
        p = off + hlen
        if hlen == 8:
            L = struct.unpack_from('<I', raw, off + 8)[0]
            base = off + 12
        else:
            L = struct.unpack_from('<H', raw, p)[0]
            base = p + 2
        ok = 0 <= L <= 4000 and base + L * 2 + 2 <= len(raw)
        end = raw[base + L * 2: base + L * 2 + 2] if ok else b''
        units = []
        if ok:
            for k in range(L):
                b0, b1 = raw[base + 2 * k], raw[base + 2 * k + 1]
                units.append(b1 if b0 == 0 else ((b0 << 8) | b1))
        dec = CL.decode(units) if ok else None
        print('  %-10s L=%d endOK=%s dec=%r' % (desc, L, end == b'\x00\x00', (dec or '')[:60]))

for off in [57280, 57302, 57318, 57328]:
    try_layout(off)
