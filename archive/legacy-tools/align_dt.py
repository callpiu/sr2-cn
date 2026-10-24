# -*- coding: utf-8 -*-
"""对齐：英文表含 Downtown 的串  vs  中文表含「城区」的串"""
import os, sys, struct, re
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
def S(ch): return IDX[ord(ch)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else ''

# ---------- 英文 ----------
v=Vpp(r"F:\sr2-cn\_ref_第三方补丁\原始基准\patch_第三方原版.vpp_pc")
d=bytes(v.read(v.find('static_US','le_strings')))
def uleb(b,i):
    s=0;sh=0
    while True:
        w=struct.unpack_from('<H',b,i)[0]; i+=2
        s|=(w&0x7FFF)<<sh; sh+=15
        if not (w&0x8000): return s,i
# 逐条从桶偏移读
HDR=12
buckets=struct.unpack_from('<H',d,HDR+4)[0]
count=struct.unpack_from('<I',d,HDR+8)[0]
print('buckets=%d count=%d'%(buckets,count))
BT=HDR+12
PTR=BT+buckets*8
recs={}
for bi in range(buckets):
    o=BT+bi*8
    n,addr=struct.unpack_from('<II',d,o)
    for k in range(n):
        off=struct.unpack_from('<I',d,PTR+(addr+k)*4)[0]
        try:
            ln,p=uleb(d,off)
            txt=d[p:p+ln*2].decode('utf-16-le')
        except Exception:
            continue
        recs.setdefault(bi,[]).append(txt)
en_all=[]
for bi in list(recs): en_all+=recs[bi]
print('英文记录 =',len(en_all))
dt=[t for t in en_all if 'Downtown' in t]
print('含 Downtown =',len(dt))
for t in sorted(set(dt)): print('  EN: %s'%t[:160])
print()

# ---------- 中文 ----------
zh=open(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc','rb').read()
pat=struct.pack('>2H',S('城'),S('区'))
hits=[];st=0
while True:
    i=zh.find(pat,st)
    if i<0:break
    hits.append(i); st=i+1
# 按记录起点去重
starts=set()
for i in hits:
    p=i
    while p>=2 and struct.unpack_from('>H',zh,p-2)[0]!=0: p-=2
    starts.add(p)
cn=set()
for p in starts:
    o=[];q=p
    while q+2<=len(zh):
        w=struct.unpack_from('>H',zh,q)[0]
        if w==0:break
        o.append(w);q+=2
    t=''.join(dec(x) for x in o).replace('\n','')
    if t: cn.add(t)
print('中文独立文本（含「城区」）= %d'%len(cn))
for t in sorted(cn): print('  CN: %s'%t[:100])