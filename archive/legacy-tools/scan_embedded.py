# -*- coding: utf-8 -*-
"""
扫描「内嵌残留」：CH 表里仍含英文专名片段的记录（含长句中间的）。
这是上一轮 v541 的漏网之鱼 —— 之前只改了「整条记录 == 该英文名」的。
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

# 上一轮已翻的 25 个名字（这些不该再出现）
DONE = ['唐人街', '三街', '帽衫镇', '昆比卡', '至乐田', '哈罗盖特', '拉萨勒',
        '雷巴多', '斯托顿', '废墟岛', '菲尔莫尔', '环能路', '哈根沙克', '狼径',
        '神奇超市', '红宝石卡尔', '法律边缘', '甜甜圈洞', '凉茶', '好牌优于一切',
        '更大的对子', '天堂限定', '天堂助手', '啤酒与小费']

# 待处理的英文专名（含内嵌）
NAMES = ['Barrio', 'Elysian Fields', 'Technically Legal', 'Sunsinger', 'Encanto',
         "Rusty's Needle", 'PHUC MI PHUC YUE', 'Sommerset', 'Saint\'s Row',
         'Saints Row', 'Wondermart', 'Carbuncle', 'Donut Holes', 'Dong Tea',
         'Hackenshack', 'Quinbecca', 'Hoodieville', 'Ruin Island', 'Filmore',
         'Lesalle', 'Rebadeaux', 'Stoughton', 'Harrowgate', 'Adept Way',
         'Fox Drive', 'Jacks or Better', 'Jacks or Higher', 'Heaven Bound',
         "Heaven's Helpers", 'Taps and Tips', 'Ezzzy', 'Zebra', 'Gaslamp',
         'Ezpata', 'Prephop', 'Rollerz', 'Little Shanghai', 'Chinatown',
         'Hotels & Marina', 'Suburbs', 'Downtown', 'Arena', 'Red Light',
         'Train Yard', 'Truck Yard', 'Los Carnales', 'Projects', 'Factories',
         'University', 'Nuke', 'Nuclear', 'Museum', 'Stilwater']

print('=== CH 表里仍含英文专名片段的记录（含内嵌）===')
hits = {}
for off, o in CH:
    if len(o) < 3: continue
    t = D(o[2:])
    if re.search(r'[\u4e00-\u9fff]', t) is None and not t.isascii():
        continue
    core = re.sub(r'\[[^\]]*\]', '', t)
    for nm in NAMES:
        if re.search(r'\b' + re.escape(nm) + r'\b', core, re.I):
            hits.setdefault(nm, []).append((off, (o[0] << 16) | o[1], core.strip(), len(o) - 2))
            break

total = 0
for nm in sorted(hits, key=lambda k: -len(hits[k])):
    v = hits[nm]
    total += len(v)
    print()
    print('### %r  %d 条' % (nm, len(v)))
    for off, h, c, ln in v[:12]:
        print('   %08X ID=%08X slots=%-3d %r' % (off, h, ln, c[:88]))
print()
print('合计记录数:', total)