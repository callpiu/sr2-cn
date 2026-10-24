# -*- coding: utf-8 -*-
"""盘点「城区 / 郊区」出现次数与上下文"""
import sys, struct, os, hashlib
sys.stdout.reconfigure(encoding='utf-8')
PATCH=r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l[0] in '/#': continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
IDX={cp:i for i,cp in enumerate(CL)}
def S(ch): return IDX[ord(ch)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '<%04X>'%s
b=open(PATCH,'rb').read()
print('md5 =',hashlib.md5(b).hexdigest(),' size =',len(b))
print()

def scan(word):
    pat=struct.pack('>%dH'%len(word),*[S(c) for c in word])
    hits=[];st=0
    while True:
        i=b.find(pat,st)
        if i<0: break
        hits.append(i); st=i+1
    return pat,hits

def ctx(at):
    #向前找到 slot 边界（对齐 2 字节），取前后各若干 slot
    p=at
    while p>=2:
        if struct.unpack_from('>H',b,p-2)[0]==0: break
        p-=2
    start=p
    o=[]
    q=p
    while q+2<=len(b):
        w=struct.unpack_from('>H',b,q)[0]
        if w==0: break
        o.append(w); q+=2
    txt=''.join(dec(x) for x in o)
    return txt

for word in ['城区','郊区']:
    pat,hits=scan(word)
    print('=== 「%s」 命中 %d 处 ==='%(word,len(hits)))
    for i in hits:
        print('  @0x%08X  %r'%(i,ctx(i)))
    print()