# -*- coding: utf-8 -*-
"""按 ID 对齐核对这些店名的中英对应，精确列出待改项"""
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

print('=== 关键店名逐条中英对照 ===')
KEYS = ['Sunsinger', 'Encanto', 'PHUC', 'Rusty', 'Somer', 'Sausage']
for off, o in CH:
    if len(o) < 3: continue
    t = D(o[2:])
    core = re.sub(r'\[[^\]]*\]', '', t).replace('\x01', ' ').strip()
    if not any(k.lower() in core.lower() for k in KEYS):
        continue
    h = (o[0] << 16) | o[1]
    us = us_by_id.get(h)
    eng = A(us[1]) if us else None
    same = '★漏翻' if eng and eng == core else ''
    print('  off=%08X ID=%08X slots=%-3d CH=%-28r US=%r %s'
          % (off, h, len(o) - 2, core[:26], (eng or '?')[:40], same))

print()
print('=== 圣徽街 4 条：英文表对应是什么 ===')
for off, o in CH:
    if len(o) < 3: continue
    t = D(o[2:])
    if '圣徽' not in t: continue
    h = (o[0] << 16) | o[1]
    us = us_by_id.get(h)
    eng = A(us[1]) if us else None
    print('  off=%08X ID=%08X CH=%r US=%r' % (off, h, D(o[2:])[:20], (eng or '?')[:60]))