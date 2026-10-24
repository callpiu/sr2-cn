# -*- coding: utf-8 -*-
"""按截图上出现的店名，精确列出 CH 表里所有对应记录（含带空格/控制字符的变体）"""
import struct, sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def D(sl):
    out = []
    for x in sl:
        if x == 0: break
        if x < 0x20: out.append('^%02X' % x)
        elif x - 0x20 < len(CL): out.append(chr(CL[x - 0x20]))
        else: out.append('?')
    return ''.join(out)

def clean(s):
    """把 ^20(空格) ^27(撇号) 等转成可读字符"""
    return re.sub(r'\^([0-9A-F]{2})', lambda m: ' ' if m.group(1) == '20' else "'", s)

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

v = Vpp(G + 'patch.vpp_pc')
CH = scan(v.read(v.find('static_CH', 'le_strings')))

KW = ['Sunsinger', 'Somer', 'PHUC', 'Encanto', 'Rusty', 'Barrio', 'Saint', 'Elysian',
      'Technically', 'Wondermart', 'Carbuncle', 'Donut', 'Dong Tea', 'Hackenshack',
      'Quinbecca', 'Hoodieville', 'Ruin Island', 'Filmore', 'Lesalle', 'Rebadeaux',
      'Stoughton', 'Harrowgate', 'Adept Way', 'Fox Drive', 'Jacks', 'Heaven', 'Taps',
      'Ezzzy', 'Gaslamp', 'Zebra', 'Prephop', 'Ezpata']

print('%-9s %-9s %-4s %s' % ('off', 'ID', 'slot', 'CH 原文（^XX = 控制字符）'))
print('-' * 118)
for off, o in CH:
    if len(o) < 3: continue
    raw = D(o[2:])
    c = clean(raw)
    if not any(k.lower() in c.lower() for k in KW):
        continue
    h = (o[0] << 16) | o[1]
    print('%-9X %08X %-4d %r' % (off, h, len(o) - 2, c[:70]))