# -*- coding: utf-8 -*-
"""
v542 方案：补全所有店名/地名残留 + 圣徽街 → 圣徒街
长度处理策略：
  - 中文比英文短 → 尾部填 0000 提前终止（安全）
  - 中文比英文长 → 用尾部已有空格 slot 顶替；不够则跳过并列报告
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

def S(ch):
    assert ord(ch) in IDX, '字表缺字: %s' % ch
    return IDX[ord(ch)] + 0x20

def pack(s):
    return b''.join(struct.pack('>H', S(c)) for c in s)

# ==== 片段替换表：只替换专名片段，保留其余文本 ====
FRAGS = [
    ("Rusty's Needle", '锈针'),
    ('PHUC MI PHUC YUE', '福记面家'),
    ('Technically Legal', '法律边缘'),
    ('Elysian Fields', '至乐田'),
    ('Sunsinger', '旭歌'),
    ('Encanto', '恩坎托'),
    ('Barrio', '唐人街'),
    ('Ezzzy 105', ' EZ 105'),
]
print('=== 片段替换表 ===')
for en, cn in FRAGS:
    print('   %-22r -> %-12r  (%d -> %d 字符)' % (en, cn, len(en), len(cn)))

# ==== 整条替换（纯英文短记录）====
WHOLE = {
    'Sunsinger': '旭歌',
    'Encanto': '恩坎托',
    'PHUC MI PHUC YUE': '福记面家',
    'Rusty\x27s Needle': '锈针',
    'Rusty\x27s Needle 1': '锈针 1',
    'Rusty\x27s Needle 2': '锈针 2',
}
print()
print('=== 整条替换 ===')
for k, v in WHOLE.items():
    print('   %-24r -> %r' % (k, v))

# ==== 字表检查 ====
print()
allc = ''.join(cn for _, cn in FRAGS) + ''.join(WHOLE.values()) + '圣徒街'
miss = sorted({c for c in allc if ord(c) not in IDX})
print('字表缺字:', miss if miss else '无')