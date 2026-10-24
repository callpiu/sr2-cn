# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp

def load(b):
    out = []
    for ln in b.decode('utf-8', 'replace').replace('\r\n', '\n').split('\n'):
        ln = ln.strip()
        if not ln or ln.startswith('//') or '=' in ln: continue
        out.append(int(ln))
    return out

vo = Vpp(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")
O = load(vo.read(vo.find('charlist_CH')))
vg = Vpp(r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc")
M = load(vg.read(vg.find('charlist_CH')))

# 观察: 源字 -> 渲染出的字形 -> 该字形在 M 里的索引
obs = [('你', '任'), ('的', '璨'), ('弟', '偶'), ('兄', '巧'), ('们', '位'),
       ('需', '雄'), ('要', '衡'), ('保', '伪'), ('护', '该')]
invM = {c: i for i, c in enumerate(M)}
invO = {c: i for i, c in enumerate(O)}

print("%-4s %-4s | %-22s | %-22s" % ("源", "渲染", "渲染字在官方表(M?)", "渲染字在modder表"))
okO = okM = 0
for src, ren in obs:
    y = invM.get(ord(ren))          # 渲染字形在 modder 表中的索引 = 引擎用的格号
    inO = invO.get(ord(ren))
    a = "%d" % inO if inO is not None else "不在"
    print("%-4s %-4s | %-22s | %-22s" % (src, ren, a, y))

print("\n=== 直接检验: 官方表[格号] 是什么字 ===")
print("%-6s %-8s %-8s %-8s %-8s" % ("源字", "格号", "官方表[格]", "modder表[格]", "渲染字"))
hitO = 0
for src, ren in obs:
    y = invM[ord(ren)]
    o = chr(O[y]) if y < len(O) else '?'
    m = chr(M[y]) if y < len(M) else '?'
    mark = "  <<< 官方表命中" if o == ren else ""
    if o == ren: hitO += 1
    print("%-6s %-8d %-8s %-8s %-8s%s" % (src, y, o, m, ren, mark))
print("\n官方表命中: %d/9" % hitO)
