# -*- coding: utf-8 -*-
"""在 static_CH 里找 DISTRICT_SUBURBS / DISTRICT_DOWNTOWN / HOOD_MISTY_LANE 的字符串
   思路：找这些 tag 键的显示值。可能在 static_CH 里以 tag 形式存放。"""
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
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '?'

G=r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v=Vpp(G+r'\patch.vpp_pc')
CH=bytes(v.read(v.find('static_CH','le_strings')))
n=len(CH)

# 1) 直接搜 ASCII tag（CH 表是 slot，ASCII 也走 slot）
print('=== 在 static_CH 搜 ASCII tag（slot 形式）===')
for tag in ['DISTRICT_SUBURBS','DISTRICT_DOWNTOWN','HOOD_MISTY_LANE','DISTRICT_SUBURBS_EXPANSION']:
    if all(has(c) for c in tag):
        pat=struct.pack('>%dH'%len(tag),*[S(c) for c in tag])
        c=CH.count(pat)
        print('  %-30s -> %d'%(tag,c))
    else:
        print('  %-30s -> 有字不在字表'%tag)
print()

# 2) 列出 CH 里所有含 DISTRICT 或 HOOD_ 的记录
def allrecs():
    res=[];i=0
    while i+2<=n:
        j=i;o=[]
        while j+2<=n:
            w=struct.unpack_from('>H',CH,j)[0]
            if w==0: break
            o.append(w);j+=2
        if j+2>n: break
        if o: res.append((i,o,''.join(dec(x) for x in o)))
        i=j+2 if o else i+2
    return res
R=allrecs()
print('static_CH 记录数 =',len(R))
print()
print('=== 含 DISTRICT 的记录 ===')
k=0
for i,o,t in R:
    if 'DISTRICT' in t.upper():
        print('  blob@0x%06X %s'%(i,t[:80])); k+=1
print('  共',k)
print()
print('=== 含 HOOD_的记录 ===')
k=0
for i,o,t in R:
    if 'HOOD' in t.upper():
        print('  blob@0x%06X %s'%(i,t[:80])); k+=1
print('  共',k)