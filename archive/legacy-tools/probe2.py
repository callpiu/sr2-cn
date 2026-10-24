# -*- coding: utf-8 -*-
"""精确定位截图那一处的「城」单字记录，看能否扩成「市郊」（+1字）
   并列出 32 条「城郊」记录的可扩展性汇总"""
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
def S(c):
    if ord(c) not in IDX: raise KeyError('%s U+%04X 不在字表'%(c,ord(c)))
    return IDX[ord(c)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '?'
b=open(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc','rb').read()
n=len(b)
SP=0x0020

def bounds(at):
    p=at
    while p>=2 and struct.unpack_from('>H',b,p-2)[0]!=0: p-=2
    st=p; q=st; o=[]
    while q+2<=n:
        w=struct.unpack_from('>H',b,q)[0]
        if w==0: break
        o.append(w); q+=2
    return st,q+2,o

print('=== 单字「城」记录（截图那处的候选）===')
pat=struct.pack('>2H',S('城'),0x0000)
st=0; hits=[]
while True:
    i=b.find(pat,st)
    if i<0: break
    hits.append(i); st=i+1
for i in hits:
    s,e,o=bounds(i)
    txt=''.join(dec(x) for x in o)
    tail=[]
    for k in range(8):
        q=e+2*k
        w=struct.unpack_from('>H',b,q)[0]
        tail.append('0x%04X'%w)
    print('  起点=0x%08X 槽数=%d 文本=%r'%(s,len(o),txt))
    print('     后续 8 slot: %s'%(' '.join(tail)))
    print('     slot 序列: %s'%(' '.join('0x%04X'%x for x in o)))
print('  共 %d 条'%len(hits))
print()

print('=== 32 条「城郊」记录尾部余量汇总 ===')
pat2=struct.pack('>2H',S('城'),S('郊'))
h2=[];st=0
while True:
    i=b.find(pat2,st)
    if i<0:break
    h2.append(i); st=i+1
recs=sorted(set(bounds(i)[:2] for i in h2))
cnt=0
for s,e in recs:
    o=[struct.unpack_from('>H',b,s+2*k)[0] for k in range((e-s)//2)]
    body=o[:-1]
    k=0
    while k<len(body) and body[len(body)-1-k]==SP: k+=1
    txt=''.join(dec(x) for x in body)
    cnt+=1
    print('  @0x%08X len=%-3d 尾空格=%d  %s'%(s,len(body),k,txt[:46]))
print('  共 %d 条'%cnt)
print()
print('=== 字表检查 ===')
for c in ['市','郊','区']:
    cp=ord(c)
    print('  %s U+%04X %s'%(c,cp,'在表内 idx=%d slot=0x%04X'%(IDX[cp],IDX[cp]+0x20) if cp in IDX else '★不在表内'))