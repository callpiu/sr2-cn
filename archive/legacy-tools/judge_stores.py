# -*- coding: utf-8 -*-
"""用英文表 ID 对齐，逐条判断哪些英文残留是「店名/地名」"""
import struct, sys, re, json
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def D(sl):
    return ''.join(chr(CL[x - 0x20]) if 0x20 <= x - 0x20 < len(CL) else '^%02X' % x for x in sl)

def A(sl):
    out = []
    for x in sl:
        if 32 <= x < 0x7f:
            out.append(chr(x))
        else:
            return None
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

v = Vpp(G + 'patch.vpp_pc')
CH = scan(v.read(v.find('static_CH', 'le_strings')))
v2 = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
US = scan(v2.read(v2.find('static_US', 'le_strings')))
us_by_id = {}
for off, o in US:
    if len(o) >= 3:
        us_by_id.setdefault((o[0] << 16) | o[1], (off, o[2:]))

left = json.load(open('F:/sr2-cn/_left_en.json', encoding='utf-8'))

# ★ 判定：英文原文里含 "店/类型" 关键词，或 ID 相邻的记录是店铺类
STORE_HINT = re.compile(
    r'Store|Shop|Tattoo|Fast Food|Burger|Pizza|Diner|Bar |Club|Brothel|'
    r'Doe Rag|X Scream|Technically|Donut|Carls|Needle|Encanto|Sunsinger|'
    r'PHUC|Wondermart|Dong Tea|Heck Hole|Disco|Records|Boots|Star|Bailey|'
    r'Eagle|Pony|Pie|Subway|Salads|Pizza|Cafe|Gym|Deli|Mall|Liqor|Liquor',
    re.I)

print('%-8s %-9s %-30s %s' % ('off', 'ID', 'CH 文本', 'US 原文'))
print('-' * 118)
for off, h, core, ln in left:
    us = us_by_id.get(h)
    eng = A(us[1]) if us else None
    if not eng:
        continue
    mark = '★店名' if STORE_HINT.search(eng) else ''
    if not mark:
        continue
    print('%-8X %-9s %-30r %r %s' % (off, '%08X' % h, core[:28], eng[:46], mark))