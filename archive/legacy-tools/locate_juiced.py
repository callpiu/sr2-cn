# -*- coding: utf-8 -*-
"""
精确定位 juiced_CH.le_strings 的每条记录，并建立与 juiced_US 的对应关系。
★ 锚点：每条记录都含 ASCII 串 "OpenSpy"（或 E-mail），用它做定位。
"""
import struct, sys, re

DIR = 'G:/SteamLibrary/steamapps/common/Saints Row 2/Mods/JUICED - Strings/'
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

def find_records(b, tag):
    """用 ASCII 锚点定位记录：向前找记录起点（0000 0000 之后），向后读文本"""
    res = []
    for anchor in (b'O\x00p\x00e\x00n\x00S\x00p\x00y', b'E\x00-\x00m\x00a\x00i\x00l',
                   b'%', b'['):
        i = 0
        while True:
            i = b.find(anchor, i)
            if i < 0: break
            # 向前：找最近的 0000 0000（记录前的终止符）
            st = i
            while st >= 8 and b[st-2:st] != b'\x00\x00':
                st -= 2
                if i - st > 200: break
            if b[st-2:st] != b'\x00\x00':
                i += 2; continue
            # 记录起点 = st - 4（ID 4 字节）
            rs = st - 4
            if rs < 0:
                i += 2; continue
            # 校验：ID 后面应是文本
            j = rs + 4
            slots = []
            while j + 2 <= len(b):
                x = struct.unpack_from('>H', b, j)[0]
                if x == 0: break
                slots.append(x); j += 2
            if b[j:j+2] != b'\x00\x00':
                i += 2; continue
            rid = struct.unpack_from('<I', b, rs)[0]
            res.append((rs, rid, slots, j + 2))
            i = j
    # 去重
    seen = {}
    for r in res:
        seen[r[0]] = r
    return sorted(seen.values(), key=lambda x: x[0])

ch = open(DIR + 'juiced_CH.le_strings', 'rb').read()
us = open(DIR + 'juiced_US.le_strings', 'rb').read()

CH = find_records(ch, 'CH')
US = find_records(us, 'US')
print('=== CH 记录 (%d) ===' % len(CH))
for rs, rid, slots, end in CH:
    print('  @%04X ID=%08X slots=%-3d %r' % (rs, rid, len(slots), dec(slots)[:62]))
print()
print('=== US 记录 (%d) ===' % len(US))
for rs, rid, slots, end in US:
    print('  @%04X ID=%08X slots=%-3d %r' % (rs, rid, len(slots), dec(slots)[:62]))