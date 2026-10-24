# -*- coding: utf-8 -*-
"""juiced_CH vs juiced_US 按 ID 对齐，列出每条错字版的英文原版"""
import struct, sys, re
sys.path.insert(0, 'F:/sr2-cn')

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def dec(sl):
    out = []
    for x in sl:
        if 0x20 <= x < 0x7f: out.append(chr(x))
        elif x < 0x20: out.append('^%02X' % x)
        elif x - 0x20 < len(CL): out.append(chr(CL[x - 0x20]))
        else: out.append('?')
    return ''.join(out)

def parse(b, st):
    recs = []
    pos = st
    while pos + 6 <= len(b):
        rid = struct.unpack_from('<I', b, pos)[0]
        j = pos + 4
        slots = []
        while j + 2 <= len(b):
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            slots.append(x); j += 2
        if b[j:j + 2] != b'\x00\x00':
            break
        recs.append((pos, rid, slots, j + 2))
        pos = j + 2
    return recs

def find_start(b, want_alpha=True):
    for st in range(0x100, len(b) - 8, 2):
        rid = struct.unpack_from('<I', b, st)[0]
        j = st + 4
        slots = []
        while j + 2 <= len(b):
            x = struct.unpack_from('>H', b, j)[0]
            if x == 0: break
            slots.append(x); j += 2
        if len(slots) >= 2 and b[j:j + 2] == b'\x00\x00':
            t = ''.join(chr(x) if 32 <= x < 0x7f else '?' for x in slots)
            if want_alpha and re.match(r'^[A-Za-z]', t):
                return st
            if not want_alpha and re.search(r'[\u4e00-\u9fff]', t):
                return st
    return None

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings/'
ch = open(G + 'juiced_CH.le_strings', 'rb').read()
us = open(G + 'juiced_US.le_strings', 'rb').read()

chs = 0x0136
uss = find_start(us, True)
print('CH 记录区起点: %s   US 记录区起点: %s' % (hex(chs) if chs else None,
                                              hex(uss) if uss else None))
CH = parse(ch, chs)
US = parse(us, uss)
print('CH %d 条, US %d 条' % (len(CH), len(US)))
usd = {rid: dec(slots) for pos, rid, slots, end in US}
print()
print('=== 逐条对齐 ===')
for pos, rid, slots, end in CH:
    print('  ID=%08X' % rid)
    print('     CH=%r' % dec(slots)[:70])
    print('     US=%r' % usd.get(rid, '★无对应')[:70])