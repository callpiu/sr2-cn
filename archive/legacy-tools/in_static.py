# -*- coding: utf-8 -*-
"""聚焦：static_CH blob 内的记录文本，查「市郊」「郊区」「城郊」以及城区相关"""
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
def S(c):
    if ord(c) not in IDX: raise KeyError('%s U+%04X 不在字表'%(c,ord(c)))
    return IDX[ord(c)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else ''
v=Vpp(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc')
CH=bytes(v.read(v.find('static_CH','le_strings')))
n=len(CH)
print('static_CH blob =',n)

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
print('记录数 =',len(R))
print()
for kw in ['市郊','郊区','城郊','市郊区']:
    ss=[S(c) for c in kw]
    pat=struct.pack('>%dH'%len(ss),*ss)
    c=CH.count(pat)
    ts=[(o,t) for i,o,t in R if kw in t]
    print('【%s】字节命中=%d  含此词的记录=%d'%(kw,c,len(ts)))
    for o,t in ts[:6]:
        print('    blob@0x%06X len=%-3d %s'%(o,len(o),t[:52]))
print()
print('=== static_CH 内所有 len<=4 的全中文记录（候选地名）===')
short={}
for i,o,t in R:
    if 0<len(t)<=4 and all(0x4e00<=ord(c)<=0x9fff for c in t):
        short.setdefault(t,[]).append(i)
for t in sorted(short):
    print('   %-8s x%d  @0x%06X'%(t,len(short[t]),short[t][0]))
print('共',len(short),'种')