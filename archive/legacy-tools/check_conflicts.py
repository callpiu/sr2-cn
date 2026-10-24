# -*- coding: utf-8 -*-
"""核对候选英文名在CH 表里是否已有中文译名（避免冲突/复用）"""
import struct, sys, re
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
TEXTS = [D(o[2:]) if len(o) > 2 else '' for o in CH]

# 候选英文名的可能已有中文译名（按 SR2 官方中文版惯例推断的关键词）
PROBES = {
    'Barrio': ['唐人街', '巴里奥'],
    'Hoodieville': ['帽衫', '连帽'],
    'Quinbecca': ['昆比卡', '昆'],
    'Elysian Fields': ['至乐田', '极乐', '乐土'],
    'Harrowgate': ['哈罗'],
    'Lesalle': ['拉萨勒', '拉萨'],
    'Rebadeaux': ['雷巴多', '里巴'],
    'Stoughton': ['斯托顿', '斯托'],
    'Ruin Island': ['废墟岛', '遗迹'],
    'Filmore': ['菲尔莫'],
    'Wondermart': ['神奇超市', '旺多'],
    'Carbuncle Carls': ['卡本克尔', '卡尔'],
    'Technically Legal': ['合法技术', '技术上合法'],
    'Donut Holes': ['甜甜圈'],
    'Dong Tea': [],
    'Jacks or Better': [],
    'Jacks or Higher': [],
    'Heaven Bound': [],
    "Heaven's Helpers": [],
    'Taps and Tips': [],
    '3rd Street': ['三街'],
    'Rollerz': ['滚轮'],
    'Adept Way': [],
    'Hackenshack': ['哈肯'],
    'Phoenix': ['凤凰'],
    "Tee'N'Ay": [],
    'APOLLO': ['阿波罗'],
    'Fox Drive': ['狐狸'],
    'Roman': ['罗曼'],
    'K6 Krukov': [],
    'Glock': ['格洛克'],
    'Holistic': [],
    'VICE': ['罪恶'],
}

print('%-22s %s' % ('英文候选', 'CH 表里可能的已有中文译名'))
print('-' * 90)
for en, cands in PROBES.items():
    hits = []
    for c in cands:
        n = sum(1 for t in TEXTS if c in t)
        if n:
            hits.append('%s(%d)' % (c, n))
    print('%-22s %s' % (en, ', '.join(hits) if hits else '(无)'))


def show(cn, limit=6):
    print()
    print('  --- 含「%s」的 CH 记录 ---' % cn)
    n = 0
    for off, o in CH:
        if len(o) < 3: continue
        t = D(o[2:])
        if cn in t:
            core = re.sub(r'\[[^\]]*\]', '', t).replace('\x01', ' ').strip()
            if len(core) <= 40:
                print('     %08X ID=%08X %r' % (off, (o[0] << 16) | o[1], core))
                n += 1
                if n >= limit: break

for cn in ['滚轮', '凤凰', '阿波罗', '唐人街', '哈肯']:
    show(cn)