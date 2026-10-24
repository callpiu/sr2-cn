# -*- coding: utf-8 -*-
"""定位暂停菜单地图界面显示的「城区 / 迷雾巷」，查英文原文"""
import sys, struct, os
sys.stdout.reconfigure(encoding='utf-8')

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
    if ord(c) not in IDX: return None
    return IDX[ord(c)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else ''
b=open(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc','rb').read()
print('patch size',len(b))

def scan(word):
    ss=[S(c) for c in word]
    if None in ss:
        print('  [%s] 有字不在字表: %s'%(word,word[ss.index(None)])); return
    pat=struct.pack('>%dH'%len(word),*ss)
    hits=[];st=0
    while True:
        i=b.find(pat,st)
        if i<0:break
        hits.append(i); st=i+1
    print('【%s】命中 %d'%(word,len(hits)))
    starts=set()
    for i in hits:
        p=i
        while p>=2 and struct.unpack_from('>H',b,p-2)[0]!=0: p-=2
        starts.add(p)
    for p in sorted(starts):
        o=[];q=p
        while q+2<=len(b):
            w=struct.unpack_from('>H',b,q)[0]
            if w==0:break
            o.append(w);q+=2
        t=''.join(dec(x) for x in o)
        print('   @0x%08X  %r'%(p,t.replace('\n','')))
    print()

for w in ['迷雾巷','城区','巷']:
    scan(w); print()

# 顺便列出表里所有独立中文记录里出现的「XX区」型地名候选
print('=== 全表独立中文记录中以「区」结尾的 ===')
# 粗略：扫所有 0x0000 分隔的 slot 记录
out=[]
i=0
n=len(b)
while i+2<=n:
    j=i;o=[]
    while j+2<=n:
        w=struct.unpack_from('>H',b,j)[0]
        if w==0: break
        o.append(w); j+=2
    if j+2<=n and len(o)>=2 and len(o)<=8:
        t=''.join(dec(x) for x in o)
        if t and t[-1]=='区' and all(ord(c)>0x2e80 for c in t):
            out.append((i,t))
    i=j+2 if o else i+2
seen={}
for i,t in out: seen.setdefault(t,0); seen[t]+=1
for t in sorted(seen): print('   %-14s x%d'%(t,seen[t]))
print('共',len(seen),'种')