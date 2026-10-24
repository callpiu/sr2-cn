# -*- coding: utf-8 -*-
"""生成待汉化清单：ID -> 中文，并算出等长/需扩容"""
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

def S(ch):
    return IDX[ord(ch)] + 0x20

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

# ==== 译名表（英 -> 中）====
# Barrio 官方中文已是「唐人街」（见 6 条已有记录）
MAP = {
    # --- 地名 / 街区 ---
    'Barrio': '唐人街',
    '3rd Street 1': '三街 1',
    '3rd Street 2': '三街 2',
    '3rd Street 3': '三街 3',
    'Hoodieville': '帽衫镇',
    'Quinbecca': '昆比卡',
    'Elysian Fields': '至乐田',
    'Harrowgate': '哈罗盖特',
    'Lesalle': '拉萨勒',
    'Rebadeaux': '雷巴多',
    'Stoughton': '斯托顿',
    'Ruin Island': '废墟岛',
    'Filmore': '菲尔莫尔',
    'Adept Way': '环能路',
    'Hackenshack': '哈根沙克',
    'Fox Drive': '狐径',
    # --- 商店 / 场所 ---
    'Wondermart 1': '神奇超市 1',
    'Carbuncle Carls': '红宝石卡尔',
    'Technically Legal': '法律边缘',
    'Donut Holes': '甜甜圈洞',
    'Dong Tea': '冬日奶茶',
    'Jacks or Better': '好牌优于一切',
    'Jacks or Higher': '更大的对子',
    'Heaven Bound': '天堂限定',
    "Heaven's Helpers": '天堂助手',
    'Taps and Tips': '啤酒与小费',
    # --- 其他漏翻的地名类 ---
    'APOLLO’S': '阿波罗',
    "Tee'N'Ay": '提安',
}

print('%-22s -> %-14s %-8s %s' % ('英文', '中文', 'slot数', '现状'))
print('-' * 100)
plan = []
for off, o in CH:
    if len(o) < 3: continue
    t = D(o[2:])
    cn = MAP.get(t)
    if not cn:
        continue
    # 查重：同英文名的所有记录
    same = [x for x, y in CH if len(y) > 2 and D(y[2:]) == t]
    # 字表可用性检查
    missing = [c for c in cn if ord(c) not in IDX]
    plan.append((off, (o[0] << 16) | o[1], t, cn, len(o) - 2, len(same), missing))
    flag = ''
    if len(same) > 1:
        flag += '★同文%d条' % len(same)
    if missing:
        flag += ' ★字表缺:%s' % ''.join(missing)
    if len(cn) != len(t):
        flag += ' 长度变(%d->%d)' % (len(t), len(cn))
    print('%-22s -> %-14s %-8d %s' % (repr(t)[:22], cn, len(o) - 2, flag or '等长'))

print()
print('合计待改记录:', len(plan))
json.dump(plan, open('F:/sr2-cn/_plan_places.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)