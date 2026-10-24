# -*- coding: utf-8 -*-
"""
★ 核心发现：static_US 的 0x84700~0x856xx 区间是「专名索引表」，
按字母序排列全部地名/店名/涂装名/外号。这是官方译名的权威对应源。
把 CH 表与这张表按 ID 对齐，即可精确判定每条该翻什么。
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
IDX = {}
for i, cp in enumerate(CL):
    IDX.setdefault(cp, i)

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

# 定位专名索引表区间
idx_rows = [(off, A(o[2:]), (o[0] << 16) | o[1]) for off, o in US
            if len(o) > 2 and A(o[2:]) and A(o[2:]).isascii() and A(o[2:]).strip()]
# 这张表的特征：短（<40 字符）、首字母大写或全大写、无句号结尾
def is_name(s):
    s = s.strip()
    if not (2 <= len(s) <= 38):
        return False
    if s.endswith(('.', ':', ',', ';')):
        return False
    if ' ' in s and len(s.split()) > 5:
        return False
    return True

names = [(off, t, h) for off, t, h in idx_rows if is_name(t)]
lo = min(o for o, t, h in names)
hi = max(o for o, t, h in names)
print('专名索引表区间: %08X .. %08X' % (lo, hi))
print('候选专名条数:', len(names))

# 只取该连续区间内的
band = [(off, t, h) for off, t, h in names if lo <= off <= hi]
band.sort()
print('区间内条数:', len(band))
print()

us_by_id = {}
for off, t, h in band:
    us_by_id.setdefault(h, (off, t))

# CH 表对齐
v = Vpp(G + 'patch.vpp_pc')
CH = scan(v.read(v.find('static_CH', 'le_strings')))

print('=== CH 表里命中「专名索引表」但仍是英文的记录（=漏翻专名）===')
todo = []
for off, o in CH:
    if len(o) < 3: continue
    t = D(o[2:])
    core = re.sub(r'\[[^\]]*\]', '', t).replace('\x01', ' ')
    core = re.sub(r'[\x02-\x1f]', ' ', core)
    # 去掉尾部编号和空格
    key = core.strip()
    key = re.sub(r'\s+\d+\s*$', '', key).strip()
    h = (o[0] << 16) | o[1]
    if h not in us_by_id:
        continue
    us = us_by_id[h][1].strip()
    if core.strip() == us or key.lower() == us.lower():
        todo.append((off, h, core.strip(), us, len(o) - 2))

print('漏翻专名:', len(todo))
print()
for off, h, core, us, ln in todo:
    print('  off=%08X ID=%08X slots=%-3d CH=%-24r US=%r' % (off, h, ln, core[:22], us[:38]))

json.dump(todo, open('F:/sr2-cn/_todo_names.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# 同时导出整张专名表供人工查
print()
print('=== 专名索引表全量（供查证）===')
for off, t, h in band:
    mark = ''
    for o2, h2, c2, u2, l2 in todo:
        if h2 == h:
            mark = '  ★CH未翻'
    print('  %08X ID=%08X %-40r%s' % (off, h, t[:38], mark))