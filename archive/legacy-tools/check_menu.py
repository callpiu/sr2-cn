# -*- coding: utf-8 -*-
"""
全面核对 Freckle Bitch's 菜单：英文原文 + 官方说明 vs 当前中文译名
"""
import struct, sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

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
            if len(out) > 600: break
        if out: res.append((i, out)); i = j + 2
        else: i += 2
    return res

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')
CH = scan(v.read(v.find('static_CH', 'le_strings')))
v2 = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
US = scan(v2.read(v2.find('static_US', 'le_strings')))

us_by_id = {}
for off, o in US:
    if len(o) > 2:
        t = A(o[2:])
        if t:
            us_by_id.setdefault((o[0] << 16) | o[1], (off, t.strip()))
ch_by_id = {}
for off, o in CH:
    if len(o) > 2:
        ch_by_id.setdefault((o[0] << 16) | o[1], []).append((off, o))

# 菜单段ID（英文表 0x66D00..0x67400 的全部记录）
print('=== Freckle Bitch\'s 菜单全项中英对照 ===')
print()
for off, o in US:
    if not (0x66D00 <= off <= 0x67450):
        continue
    if len(o) < 3:
        continue
    h = (o[0] << 16) | o[1]
    eng = A(o[2:])
    if not eng or not eng.strip():
        continue
    eng = eng.strip()
    rows = ch_by_id.get(h)
    if not rows:
        continue
    cn = D(rows[0][1][2:]).strip()
    # 说明：下一条记录
    k = US.index((off, o))
    desc = ''
    if k + 1 < len(US):
        d = A(US[k + 1][1][2:]) if len(US[k + 1][1]) > 2 else None
        if d and len(d) > 12:
            desc = d.strip()
    print('  %-24r -> %-22r' % (eng, cn))
    if desc:
        print('        说明: %s' % desc[:96])