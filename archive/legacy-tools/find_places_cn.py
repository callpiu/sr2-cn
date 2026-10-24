# -*- coding: utf-8 -*-
"""聚焦：找出static_CH 里已存在中文译名的地名/商店，与漏翻英文对照"""
import struct, sys, json, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/'
CL = []
for l in open('F:/sr2-cn/_cl_now.txt', 'rb').read().decode('latin1').split('\n'):
    s = l.strip()
    if s.isdigit():
        CL.append(int(s))

def D(slots):
    out = []
    for x in slots:
        if x == 0: break
        if x < 0x20: out.append('\x01')
        elif x - 0x20 < len(CL): out.append(chr(CL[x - 0x20]))
        else: out.append('?')
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
print('CH records', len(CH))

# 收集全部已汉化文本（含中文）
cn_all = []
for off, o in CH:
    if len(o) < 3: continue
    t = D(o[2:])
    if re.search(r'[\u4e00-\u9fff]', t):
        cn_all.append((off, (o[0] << 16) | o[1], t))
print('含中文记录', len(cn_all))

# 找地名/商店类中文：含"区/街/店/超市/酒吧/餐厅/咖啡/夜总会/酒馆/诊所/银行/加油站/车库"等
PLACE_KW = ['区', '街', '店', '超市', '酒吧', '餐厅', '咖啡', '夜总会', '酒馆',
            '诊所', '银行', '加油站', '车库', '当铺', '理发', '旅馆', '酒店', '广场', '中心', '市场']
print()
print('=== CH 表里现有的「地名/商店」类中文译名（含这些关键词）===')
n = 0
places = []
for off, h, t in cn_all:
    core = re.sub(r'\[[^\]]*\]', '', t).replace('\x01', ' ').strip()
    if 2 <= len(core) <= 16 and any(k in core for k in PLACE_KW):
        n += 1
        places.append((off, h, core))
for off, h, core in places:
    print('  %08X ID=%08X %r' % (off, h, core))
print('total', n)