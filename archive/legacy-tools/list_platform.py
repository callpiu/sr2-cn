# -*- coding: utf-8 -*-
"""列出 platform_pc_CH 全部短记录（OpenSpy 界面文本所在表）"""
import struct, sys, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def D(sl):
    out = []
    for x in sl:
        if x < 0x20:
            out.append(chr(x))
        elif x - 0x20 < len(CL):
            out.append(chr(CL[x - 0x20]))
        else:
            out.append('?')
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

def A(sl):
    out = []
    for x in sl:
        if 32 <= x < 0x7f:
            out.append(chr(x))
        else:
            return None
    return ''.join(out)

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
v = Vpp(G + 'patch.vpp_pc')
R = scan(v.read(v.find('platform_pc_CH', 'le_strings')))
print('platform_pc_CH 共 %d 条' % len(R))

# 英文表对照
v2 = Vpp('F:/sr2-cn/_ref_第三方补丁/原始基准/patch_第三方原版.vpp_pc')
try:
    US = scan(v2.read(v2.find('platform_pc_US', 'le_strings')))
    us_by_id = {}
    for off, o in US:
        if len(o) > 2:
            t = A(o[2:])
            if t:
                us_by_id.setdefault((o[0] << 16) | o[1], t.strip())
except Exception as e:
    print('US 表读取失败:', e)
    us_by_id = {}

print()
print('=== 短记录（<=10 slot）===')
print('%-9s %-9s %-4s %-20s %s' % ('off', 'ID', 'slot', '中文', '英文'))
print('-' * 92)
for off, o in R:
    if len(o) < 3:
        continue
    t = D(o[2:]).strip()
    if not (0 < len(t) <= 10):
        continue
    h = (o[0] << 16) | o[1]
    print('%-9X %08X %-4d %-20r %r' % (off, h, len(o) - 2, t, us_by_id.get(h, '')))