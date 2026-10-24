# -*- coding: utf-8 -*-
"""在所有 CH 表 + 所有 txt 表里搜 DISTRICT_SUBURBS / DISTRICT_DOWNTOWN / HOOD_MISTY_LANE"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l[0] in '/#': continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
IDX={cp:i for i,cp in enumerate(CL)}
def has(c): return ord(c) in IDX
def S(c): return IDX[ord(c)]+0x20

G=r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v=Vpp(G+r'\patch.vpp_pc')
TAGS=['DISTRICT_SUBURBS','DISTRICT_DOWNTOWN','HOOD_MISTY_LANE','DISTRICT_SUBURBS_EXPANSION']

def scan_slot(blob,tag):
    if not all(has(c) for c in tag): return None
    pat=struct.pack('>%dH'%len(tag),*[S(c) for c in tag])
    return blob.count(pat)
def scan_ascii(blob,tag):
    return blob.count(tag.encode('ascii'))

print('=== CH 表（slot 编码）===')
for t in v.entries():
    if t['ext']!='le_strings': continue
    if not (t['name'].endswith('_CH')): continue
    try:
        d=bytes(v.read(t))
    except Exception:
        continue
    line='  %-22s size=%-8d'%(t['name'],len(d))
    res=[]
    for tag in TAGS:
        c=scan_slot(d,tag)
        res.append('%s=%s'%(tag[:14],c))
    print(line+'  '+'  '.join(res))

print()
print('=== 所有 txt 表（ASCII 原样）===')
for t in v.entries():
    if t['ext'] not in ('txt',''): continue
    if t['size']>3_000_000: continue
    try: d=bytes(v.read(t))
    except Exception: continue
    hits=[]
    for tag in TAGS:
        c=d.count(tag.encode('ascii'))
        if c: hits.append('%s=%d'%(tag,c))
    if hits:
        print('  %-24s %s'%(t['name'],'  '.join(hits)))