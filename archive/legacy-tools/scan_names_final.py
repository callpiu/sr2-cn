# -*- coding: utf-8 -*-
"""
v543：按 US 表专名名录，精确列出「地名段 + 店名段」里 CH 侧仍为英文的所有项。
"""
import struct, sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))
IDX = {}
for i, cp in enumerate(CL):
    IDX.setdefault(cp, i)

def D(sl):
    return ''.join(chr(CL[x - 0x20]) if 0x20 <= x - 0x20 < len(CL) else '^%02X' % x for x in sl)

def clean(s):
    return re.sub(r'\^([0-9A-F]{2})',
                  lambda m: ' ' if m.group(1) == '20' else chr(int(m.group(1), 16)), s)

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

v2 = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
US = scan(v2.read(v2.find('static_US', 'le_strings')))

# 地名段（含 Hood/District/地点）
PLACE_BANDS = [(0x84746, 0x85000), (0x85140, 0x85200)]
# 店名段（与 RUSTY'S NEEDLE / PHUC MI PHUC YUE 同组的服装/店铺名）
STORE_BAND = (0x6A000, 0x6A600)
# 地点描述段（Freckle Bitch's 与 'Barrio - On Track' 同组）
SPOT_BAND = (0x27400, 0x27600)

bands = PLACE_BANDS + [STORE_BAND, SPOT_BAND]
name_us = {}
for off, o in US:
    if len(o) < 3: continue
    if not any(a <= off <= b for a, b in bands): continue
    t = A(o[2:])
    if t and t.strip():
        name_us.setdefault((o[0] << 16) | o[1], (off, t.strip()))

print('专名候选（地名段+店名段+地点段）:', len(name_us))

v = Vpp(G + 'patch.vpp_pc')
CH = scan(v.read(v.find('static_CH', 'le_strings')))

print()
print('=== CH 侧仍是英文的漏翻项 ===')
todo = []
for off, o in CH:
    if len(o) < 3: continue
    h = (o[0] << 16) | o[1]
    if h not in name_us:
        continue
    ch = clean(D(o[2:])).strip()
    ch = re.sub(r'\s+', ' ', ch)
    eng = name_us[h][1]
    if not ch.isascii():
        continue
    key = re.sub(r'\s+\d+\s*$', '', ch).strip().lower()
    ekey = re.sub(r'\s+\d+\s*$', '', eng).strip().lower()
    if key == ekey:
        todo.append((off, h, ch, eng, len(o) - 2, name_us[h][0]))

# 按英文名聚合
agg = {}
for off, h, ch, eng, ln, uoff in todo:
    agg.setdefault(eng, []).append((off, h, ch, ln, uoff))

for eng in sorted(agg):
    v = agg[eng]
    print('  %-34r %d 条  (US@%08X)' % (eng[:32], len(v), v[0][4]))
    for off, h, ch, ln, uoff in v[:8]:
        print('       %08X ID=%08X slot=%-3d %r' % (off, h, ln, ch[:40]))

print()
print('合计:', sum(len(x) for x in agg.values()), '条 /', len(agg), '个名字')