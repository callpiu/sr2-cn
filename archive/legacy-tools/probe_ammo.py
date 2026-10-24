# -*- coding: utf-8 -*-
"""盘点 散筒枪/霰弹枪、火料/火药、填药/弹药 的分布 + 尾部余量"""
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
def has(c): return ord(c) in IDX
def S(c):
    if not has(c): raise KeyError('%s U+%04X 不在字表'%(c,ord(c)))
    return IDX[ord(c)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else ''
b=open(PATCH,'rb').read()
n=len(b)
print('md5 =',hashlib.md5(b).hexdigest(),'size =',len(b))
print()
SP=0x0020
print('=== 字表可用性 ===')
for c in ['散','筒','霰','弹','枪','火','料','药','填','子','弹']:
    cp=ord(c)
    print('  %s U+%04X %s'%(c,cp,'slot=0x%04X'%(IDX[cp]+0x20) if cp in IDX else '★不在字表'))
print()

def bounds(at):
    p=at
    while p>=2 and struct.unpack_from('>H',b,p-2)[0]!=0: p-=2
    st=p; q=st; o=[]
    while q+2<=n:
        w=struct.unpack_from('>H',b,q)[0]
        if w==0: break
        o.append(w); q+=2
    return st,q+2,o

def scan(word):
    if not all(has(c) for c in word):
        miss=[c for c in word if not has(c)]
        print('【%s】★ 有字不在字表: %s'%(word,miss)); return
    pat=struct.pack('>%dH'%len(word),*[S(c) for c in word])
    hits=[];st=0
    while True:
        i=b.find(pat,st)
        if i<0:break
        hits.append(i); st=i+1
    recs=sorted(set(bounds(i)[:2] for i in hits))
    print('【%s】字节命中=%d独立记录=%d'%(word,len(hits),len(recs)))
    slack=[]
    for s,e in recs:
        o=[struct.unpack_from('>H',b,s+2*k)[0] for k in range((e-s)//2)]
        body=o[:-1]
        k=0
        while k<len(body) and body[len(body)-1-k]==SP: k+=1
        txt=''.join(dec(x) for x in body)
        slack.append(k)
        print('   @0x%08X len=%-3d尾空格=%d  %s'%(s,len(body),k,txt.replace('\n','')[:54]))
    print('   →有尾空格余量的记录: %d/%d'%(sum(1 for x in slack if x>0),len(recs)))
    print()
    return hits,recs

for w in ['散筒枪','霰弹枪','火料','火药','填药','弹药','弹药填料','散弹']:
    scan(w)