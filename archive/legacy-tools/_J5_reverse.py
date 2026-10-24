# -*- coding: utf-8 -*-
"""反查：把屏幕乱码字映射回 charlist 索引，再对比正确文本的索引，
算出真实 unit 值，然后在各 le_strings 里搜索该 unit 序列。"""
import sys, struct, os
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp
from sr2strings import CharList

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(G + '/patch.vpp_pc')
txt = v.read(v.find('charlist_CH', 'txt')).decode()
ns = [int(t) for t in txt.split() if t.lstrip('-').isdigit()]
if ns and ns[0] == len(ns) - 1:
    ns = ns[1:]
CL = CharList(ns)

# 屏幕乱码 -> 期望字
pairs = [
    ('任', '你'), ('璨', '的'), ('偶', '弟'), ('巧', '兄'), ('位', '们'),
    ('雄', '需'), ('衡', '要'), ('伪', '保'), ('该', '护'),
]
print('屏幕字 -> 该字在 CL 的索引 (idx0-based, unit值)')
for garbled, want in pairs:
    gi = [i for i, c in enumerate(CL.body) if c == ord(garbled)]
    wi = [i for i, c in enumerate(CL.body) if c == ord(want)]
    print('  %s(U+%04X) idx=%s   |   期望 %s(U+%04X) idx=%s'
          % (garbled, ord(garbled), gi, want, ord(want), wi))

# 反过来：正确文本"你的"的 CL 索引
for w in '你的弟兄们需要保护':
    i = [i for i, c in enumerate(CL.body) if c == ord(w)]
    print('  %s -> idx %s' % (w, i))
