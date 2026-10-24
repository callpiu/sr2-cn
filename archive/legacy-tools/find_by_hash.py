# -*- coding: utf-8 -*-
"""按用户提供的 hash (h=1896 / h=1EEE) 反查所有 le_strings 表里的记录"""
import struct, sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def dec(sl):
    out = []
    for x in sl:
        if x < 0x20: out.append(chr(x))
        elif x - 0x20 < len(CL): out.append(chr(CL[x - 0x20]))
        else: out.append('?')
    return ''.join(out)

def A(sl):
    out = []
    for x in sl:
        if 32 <= x < 0x7f: out.append(chr(x))
        else: return None
    return ''.join(out)

def scan(b):
    res = []; i = 0; n = len(b)
    while i + 2 <= n:
        j = i; out = []
        while j + 2 <= n:
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            out.append(x); j += 2
            if len(out) > 800: break
        if out: res.append((i, out)); i = j + 2
        else: i += 2
    return res

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
TARGETS = {0x1896, 0x1EEE}

for vppf in ['patch.vpp_pc', 'common.vpp_pc']:
    v = Vpp(G + vppf)
    for e in v.entries():
        if e['ext'] != 'le_strings':
            continue
        blob = v.read(e)
        for off, o in scan(blob):
            if len(o) < 3:
                continue
            h1 = o[0]
            h2 = o[1]
            full = (h1 << 16) | h2
            if h2 in TARGETS or h1 in TARGETS or (full & 0xFFFF) in TARGETS:
                t = dec(o[2:])
                en = A(o[2:])
                print('%-22s off=%08X ID=%08X (hi=%04X lo=%04X) CH=%r EN=%r'
                      % (e['name'], off, full, h1, h2, t[:60], en[:60] if en else ''))

print()
print('=== 顺便：全表搜含 OpenSpy 的 le_strings 记录（再确认一次）===')
for vppf in ['patch.vpp_pc', 'common.vpp_pc']:
    v = Vpp(G + vppf)
    for e in v.entries():
        if e['ext'] != 'le_strings':
            continue
        blob = v.read(e)
        for off, o in scan(blob):
            if len(o) < 3:
                continue
            t = dec(o[2:])
            if 'OpenSpy' in t or 'OpenSpy' in str(A(o[2:])):
                print('%-22s off=%08X ID=%08X %r' % (e['name'], off,
                      (o[0] << 16) | o[1], t[:70]))