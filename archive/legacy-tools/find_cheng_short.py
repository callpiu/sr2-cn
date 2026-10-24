# -*- coding: utf-8 -*-
"""在 patch.vpp_pc 全文扫「城」单字独立记录 / 短地名记录"""
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
def S(c): return IDX[ord(c)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else ''
b=open(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc','rb').read()
n=len(b)

s=S('城')
pat=struct.pack('>H',s)
hits=[];st=0
while True:
    i=b.find(pat,st)
    if i<0:break
    hits.append(i); st=i+1
print('「城」字节命中 %d'%len(hits))

# 抽出所有 1~6 字、且全是 CJK 的独立记录（限定在 static_CH 文本区附近）
# 文本区大致 0x1C00000 ~ 0x2F00000
def rec_at(i):
    p=i
    while p>=2 and struct.unpack_from('>H',b,p-2)[0]!=0: p-=2
    q=p;o=[]
    while q+2<=n:
        w=struct.unpack_from('>H',b,q)[0]
        if w==0:break
        o.append(w);q+=2
    return p,''.join(dec(x) for x in o)

short={}
for i in hits:
    p,t=rec_at(i)
    t=t.replace('\n','')
    if 0<len(t)<=6 and all(0x4e00<=ord(c)<=0x9fff for c in t):
        short.setdefault(t,[]).append(p)
print()
print('=== 含「城」的短中文记录（≤6字，全CJK）===')
for t in sorted(short):
    print('   %-8s x%d  @%s'%(t,len(short[t]),' '.join('0x%08X'%x for x in sorted(set(short[t]))[:4])))

# 另外找 2 字地名候选表（地图区域名常 2~3 字）：扫整个 CH 区的短记录太多，
# 改为列出所有含「区」的 ≤4 字中文记录
print()
print('=== 含「区」的 ≤4 字中文记录 ===')
s2=struct.pack('>H',S('区'))
h2=[];st=0
while True:
    i=b.find(s2,st)
    if i<0:break
    h2.append(i); st=i+1
print('「区」字节命中 %d'%len(h2))
d={}
for i in h2:
    p,t=rec_at(i)
    t=t.replace('\n','')
    if 0<len(t)<=4 and all(0x4e00<=ord(c)<=0x9fff for c in t):
        d.setdefault(t,[]).append(p)
for t in sorted(d):
    print('   %-6s x%d  @%s'%(t,len(d[t]),' '.join('0x%08X'%x for x in sorted(set(d[t]))[:3])))