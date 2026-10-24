# -*- coding: utf-8 -*-
"""定位字幕记录：从每个 ASCII 锚点向前找记录头，向后解 CJK，搜索关键字。"""
import sys, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp
from sr2strings import CharList

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(G + '/patch.vpp_pc')
raw = v.read(v.find('static_CH', 'le_strings'))
txt = v.read(v.find('charlist_CH', 'txt')).decode()
ns = [int(t) for t in txt.split() if t.lstrip('-').isdigit()]
if ns and ns[0] == len(ns) - 1:
    ns = ns[1:]
CL = CharList(ns)
n = len(raw)

def dec_units(base, limit=600):
    out = []
    o = base
    while o + 1 < n and len(out) < limit:
        b0, b1 = raw[o], raw[o + 1]
        if b0 == 0 and b1 == 0:
            break
        u = b1 if b0 == 0 else ((b0 << 8) | b1)
        if u < 0x100:
            out.append(chr(u))
        elif u < len(CL.body):
            out.append(chr(CL.body[u]))
        else:
            out.append('<?%d>' % u)
        o += 2
    return ''.join(out)

# 全局扫描：每个偶数偏移尝试解码，找关键字
KEYS = ['直升机', '突击', '弟兄们', '保护', '面包车', '停靠', '生意', '迷雾巷']
found = []
for o in range(0, n - 2, 2):
    b0, b1 = raw[o], raw[o + 1]
    if b0 == 0 and b1 in (0,):
        continue
    u = b1 if b0 == 0 else ((b0 << 8) | b1)
    # 快速过滤：只从 CJK 候选起点开始试
    if 0x100 <= u < len(CL.body) and CL.body[u] in (0x4F60, 0x4FDD, 0x76F4, 0x9700, 0x4EBA, 0x8F66, 0x505C, 0x751F):  # 你保直需人车停生
        s = dec_units(o, 80)
        if any(k in s for k in KEYS):
            found.append((o, s))

print('命中 %d 个起点' % len(found))
seen = set()
for o, s in found:
    if s[:20] in seen:
        continue
    seen.add(s[:20])
    print('@%7d  %s' % (o, s[:90]))
    if len(seen) > 40:
        break
