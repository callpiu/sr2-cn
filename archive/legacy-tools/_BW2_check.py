# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp

def load(b):
    out = []
    for ln in b.decode('utf-8', 'replace').replace('\r\n', '\n').split('\n'):
        ln = ln.strip()
        if not ln or ln.startswith('//'): continue
        if ln.lower().startswith('count='): continue
        if '=' in ln: continue
        out.append(int(ln))
    return out

vo = Vpp(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")
off_cl = load(vo.read(vo.find('charlist_CH')))
print("官方 charlist_CH 项数 =", len(off_cl))
print("  升序?", all(off_cl[i] < off_cl[i+1] for i in range(len(off_cl)-1)))
print("  头 8:", off_cl[:8], " 尾 8:", off_cl[-8:])

vg = Vpp(r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc")
mod_cl = load(vg.read(vg.find('charlist_CH')))
print("modder charlist_CH 项数 =", len(mod_cl))

inv_off = {c: i for i, c in enumerate(off_cl)}
inv_mod = {c: i for i, c in enumerate(mod_cl)}

PAIRS = [('你', 336), ('的', 1784), ('弟', 410), ('兄', 967), ('们', 362),
         ('需', 2656), ('要', 2268), ('保', 354), ('护', 2342)]
print("\n%-4s %-6s %-8s %-8s %-8s" % ("字", "码点", "渲染格", "官方索引", "modder索引"))
hit = 0
for c, y in PAIRS:
    cp = ord(c)
    a = inv_off.get(cp)
    b = inv_mod.get(cp)
    mark = "  <<< 命中" if a == y else ""
    if a == y: hit += 1
    print("%-4s U+%04X %-8d %-8s %-8s%s" % (c, cp, y, a, b, mark))
print("\n官方索引命中: %d/9" % hit)
