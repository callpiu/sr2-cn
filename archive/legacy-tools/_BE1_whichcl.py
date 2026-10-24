# -*- coding: utf-8 -*-
"""哪个字符表能把渲染索引对上？"""
import sys, struct, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0, '.')
from _vpp import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
gv = Vpp(G)

# 观察到的: 显示字 -> 其在实际图集中的 cell 索引
shown = [('任',336),('璨',1784),('偶',410),('巧',967),('位',362),('雄',2656),('衡',2268),('伪',354),('该',2342)]
# 正确的源字
src   = ['你','的','弟','兄','们','需','要','保','护']
# 记录里的 slot
slots = [403,1868,1067,454,364,2699,2328,423,1222]

def parse_text(buf):
    out=[]
    for ln in buf.decode('latin-1').splitlines():
        s=ln.strip()
        if not s or s.startswith('//') or s.startswith('count'): continue
        try: out.append(int(s))
        except: pass
    return out

tables = {}
for e in gv.entries():
    if e['name'].lower().startswith('charlist') or e['name'].lower().endswith('charlist'):
        try:
            t = parse_text(gv.read(e))
            if t: tables[e['name']] = t
        except Exception as ex:
            print('skip', e['name'], ex)

# 也用当前磁盘上的 charlist_CH（已含 count 行）
for name, t in tables.items():
    inv = {}
    for i,c in enumerate(t):
        inv.setdefault(c, i)
    idxs = [inv.get(ord(s), -1) for s in src]
    shownidx = [s[1] for s in shown]
    match = sum(1 for a,b in zip(idxs, shownidx) if a==b)
    print(f'{name:16s} n={len(t):5d} 你@{inv.get(ord("你"),-1):5d} 的@{inv.get(ord("的"),-1):5d} 弟@{inv.get(ord("弟"),-1):5d} 匹配{matches if False else match}/9')
    print('     idxs   ', idxs)
print('  observed   ', [s[1] for s in shown])
print()
# 反过来：如果引擎用的是 slot-32 之外的其他常数？
print('源字 slot slot-32  显示字 显示字在该表索引')
cl = tables.get('charlist_CH')
for (s,sl,(sh,shi)) in zip(src, slots, shown):
    print(f'  {s}  {sl:5d} {sl-32:5d}   {sh}   {shi:5d}')
