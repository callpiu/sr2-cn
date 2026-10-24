# -*- coding: utf-8 -*-
"""
权威专名名录对齐：US 表 0x84746..0x85200 是完整地名表（Hood/District/地点）。
把 CH 表按 ID 对齐，逐条列出「CH 侧仍是英文」的漏翻项。
"""
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

v2 = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
US = scan(v2.read(v2.find('static_US', 'le_strings')))

# 收集专名表：ID -> 英文原文
name_us = {}
for off, o in US:
    if len(o) < 3: continue
    h = (o[0] << 16) | o[1]
    t = A(o[2:])
    if t and t.strip():
        name_us.setdefault(h, (off, t.strip()))
print('US 可用 ID 索引:', len(name_us))

v = Vpp(G + 'patch.vpp_pc')
CH = scan(v.read(v.find('static_CH', 'le_strings')))

# CH 里所有"仍是纯英文"的短记录（<=12 slot，无 format 标签）
sus = []
for off, o in CH:
    if len(o) < 3: continue
    raw = D(o[2:])
    if '[' in raw or '\x01' in raw and any(chr(x) in raw for x in range(2, 0x20)):
        continue
    core = raw.strip()
    if not core or len(core) > 16: continue
    if not core.isascii(): continue
    if len(core) < 3: continue
    h = (o[0] << 16) | o[1]
    us = name_us.get(h)
    if not us: continue
    eng = us[1]
    if core.lower() == eng.lower() or core.lower().rstrip('0123456789 ') == eng.lower().rstrip('0123456789 '):
        sus.append((off, h, core, eng, len(o) - 2))

print('ID 对齐后仍为英文的短记录:', len(sus))
print()
print('%-9s %-9s %-4s %-26s %s' % ('off', 'ID', 'slot', 'CH 文本', 'US 原文'))
print('-' * 100)
for off, h, core, eng, ln in sorted(sus, key=lambda x: x[2]):
    print('%-9X %08X %-4d %-26r %r' % (off, h, ln, core[:24], eng[:44]))

json.dump([[a, b, c, d, e] for a, b, c, d, e in sus],
          open('F:/sr2-cn/_sus_shop.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)