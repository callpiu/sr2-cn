# -*- coding: utf-8 -*-
"""
最终判定：把 US 表 0x84600..0x85700 的「专名名录」全部按 ID 与 CH 表对齐。
分三类输出：
  A) CH 已汉化（正常）
  B) CH 仍是英文（漏翻）—— 这些就是要改的
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
    out = []
    for x in sl:
        if x == 0: break
        if x < 0x20: out.append(' ')
        elif x - 0x20 < len(CL): out.append(chr(CL[x - 0x20]))
        else: out.append('?')
    return ''.join(out)

def A(sl):
    out = []
    for x in sl:
        if 32 <= x < 0x7f: out.append(chr(x))
        else: return None
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
v = Vpp(G + 'patch.vpp_pc')
CH = scan(v.read(v.find('static_CH', 'le_strings')))

# US 专名名录（含地名 + 店名 + 涂装名）
BAND = (0x84600, 0x85800)
name_us = {}
for off, o in US:
    if len(o) < 3: continue
    if not (BAND[0] <= off <= BAND[1]): continue
    t = A(o[2:])
    if t and t.strip():
        name_us.setdefault((o[0] << 16) | o[1], (off, t.strip()))
print('US 专名名录条数:', len(name_us))

# CH 侧：凡 ID 命中名录
done = []
miss = []
for off, o in CH:
    if len(o) < 3: continue
    h = (o[0] << 16) | o[1]
    if h not in name_us:
        continue
    uoff, eng = name_us[h]
    ch = D(o[2:]).strip()
    ch_norm = re.sub(r'\s+', ' ', ch)
    en_norm = re.sub(r'\s+', ' ', eng)
    has_cn = bool(re.search(r'[\u4e00-\u9fff]', ch))
    if has_cn:
        done.append((off, h, ch, eng, len(o) - 2))
    elif ch_norm.lower().rstrip('0123456789 ').strip() == en_norm.lower().rstrip('0123456789 ').strip():
        miss.append((off, h, ch, eng, len(o) - 2))

print('已汉化:', len(done))
print('仍为英文（漏翻）:', len(miss))
print()
print('==== 漏翻清单 ====')
print('%-9s %-9s %-4s %-30s %s' % ('off', 'ID', 'slot', 'CH', 'US'))
print('-' * 110)
for off, h, ch, eng, ln in sorted(miss, key=lambda x: x[3]):
    print('%-9X %08X %-4d %-30r %r' % (off, h, ln, ch[:28], eng[:48]))

json.dump({'miss': [[a, b, c, d, e] for a, b, c, d, e in miss],
           'done': [[a, b, c, d, e] for a, b, c, d, e in done]},
          open('F:/sr2-cn/_name_align.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)