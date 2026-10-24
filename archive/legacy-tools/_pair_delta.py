# -*- coding: utf-8 -*-
"""逐一验证 9 对观测乱码，找每对所需的 delta（在 patch_CH 2795 表上）。
若 delta 恒定 -> 常量偏移；若变化 -> 重排。
"""
import sys, os, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'

def load_cl(vp, name):
    buf = vp.read(vp.find(name, 'txt'))
    end = buf.find(b'//ENDOFFILE')
    if end < 0:
        end = len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]

v = Vpp(os.path.join(G, 'patch.vpp_pc'))
cl = load_cl(v, 'charlist_CH')
idx = {c: i for i, c in enumerate(cl)}

# 观测乱码对
pairs = [('你', '任'), ('的', '璨'), ('弟', '偶'), ('兄', '巧'), ('们', '位'),
         ('需', '雄'), ('要', '衡'), ('保', '伪'), ('护', '该')]
print('%-4s %-4s %-8s %-8s %-8s' % ('src', 'dst', 'src_idx', 'dst_idx', 'idx差(dst-src)'))
for s, d in pairs:
    si = idx.get(ord(s)); di = idx.get(ord(d))
    print('%-4s %-4s %-8s %-8s %s' % (s, d, si, di, (di - si) if (si is not None and di is not None) else '?'))

# 也验证：REC2 全 22 字，若渲染用 glyph 直接索引 charlist[glyph] 会得到什么
rec2_slots = [403,1868,1067,454,364,2328,510,613,2389,502,1995,1824,1159,2822,423,1222,356,364,460,2563,2312,511]
true_txt = '你的弟兄们要出去谈几笔生意，保护他们免遭袭击'
print('\nREC2 原本:', true_txt)
for label, f in [('charlist[slot]', lambda s: cl[s] if s < len(cl) else -1),
                 ('charlist[slot-0x20]', lambda s: cl[s-0x20] if 0 <= s-0x20 < len(cl) else -1)]:
    out = ''.join(chr(f(s)) if f(s) > 0 else '?' for s in rec2_slots)
    print('%-22s -> %s' % (label, out))
