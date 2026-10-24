# -*- coding: utf-8 -*-
"""查中文表里「郊」「区」「主城区」的分布，以及相关地名串"""
import sys, struct
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
def S(ch):
    if ord(ch) not in IDX: raise KeyError('%s(U+%04X) 不在字表'%(ch,ord(ch)))
    return IDX[ord(ch)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else ''
zh=open(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc','rb').read()

def scan(word,label=None):
    pat=struct.pack('>%dH'%len(word),*[S(c) for c in word])
    hits=[];st=0
    while True:
        i=zh.find(pat,st)
        if i<0:break
        hits.append(i); st=i+1
    starts=set()
    for i in hits:
        p=i
        while p>=2 and struct.unpack_from('>H',zh,p-2)[0]!=0: p-=2
        starts.add(p)
    print('【%s】字节命中 %d 处 / 独立记录 %d 条'%(label or word,len(hits),len(starts)))
    ts=set()
    for p in starts:
        o=[];q=p
        while q+2<=len(zh):
            w=struct.unpack_from('>H',zh,q)[0]
            if w==0:break
            o.append(w);q+=2
        t=''.join(dec(x) for x in o).replace('\n','').replace('\x00','')
        if t: ts.add(t)
    return ts

print('=== 1) 「郊」单字 ===')
t1=scan('郊')
for t in sorted(t1)[:40]: print('   %s'%t[:110])
print()
print('=== 2) 「主城区」 ===')
t2=scan('主城区')
print()
print('=== 3) 裸「城区」（前面不是「主」）===')
pat=struct.pack('>2H',S('城'),S('区'))
mp=struct.pack('>2H',S('主'),S('城'))
cnt=0
st=0
while True:
    i=zh.find(pat,st)
    if i<0:break
    prev=struct.unpack_from('>H',zh,i-2)[0] if i>=2 else 0
    if prev!=S('主'):
        p=i
        while p>=2 and struct.unpack_from('>H',zh,p-2)[0]!=0: p-=2
        o=[];q=p
        while q+2<=len(zh):
            w=struct.unpack_from('>H',zh,q)[0]
            if w==0:break
            o.append(w);q+=2
        t=''.join(dec(x) for x in o).replace('\n','')
        print('   @0x%08X %s'%(i,t[:110])); cnt+=1
    st=i+1
print('   裸「城区」= %d 处'%cnt)