# -*- coding: utf-8 -*-
"""chunk079 里 0x1F9E48 附近到底是什么结构？
   观察：全表是 [u16][0000] 交替。统计该 chunk 内 CJK slot 的分布"""
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

S1=S('城'); S2=S('郊'); S3=S('区'); SM=S('市')
print('slot: 城=0x%04X 郊=0x%04X 区=0x%04X 市=0x%04X'%(S1,S2,S3,SM))
print()
# 全文件找 CJK slot（0x20..0x20+2794）连续成串（>=2 字）的区域 = 真文本区
def is_cjk(w): return 0x20<=w<0x20+len(CL) and CL[w-0x20]>0x2E80
print('=== 全文件中「连续>=2 个 CJK slot」的文本区分布（前 40 段）===')
segs=[]; i=0; n=len(b)
while i+2<=n:
    w=struct.unpack_from('>H',b,i)[0]
    if is_cjk(w):
        j=i; o=[]
        while j+2<=n:
            x=struct.unpack_from('>H',b,j)[0]
            if not is_cjk(x): break
            o.append(x); j+=2
        if len(o)>=2: segs.append((i,j,''.join(dec(x) for x in o)))
        i=j
    else:
        i+=2
print('文本段总数 =',len(segs))
from collections import Counter
c=Counter()
for s,e,t in segs:
    c[s>>16]+=1
for k,v in sorted(c.items()):
    print('  0x%08X-0x%08X 段数=%d'%(k<<16,(k+1)<<16,v))
print()
print('=== 含「城」且长度<=3 的短文本段 ===')
for s,e,t in segs:
    if '城' in t and len(t)<=3:
        print('  @0x%08X  %r'%(s,t))
print()
print('=== 含「市」的短文本段 ===')
for s,e,t in segs:
    if '市' in t and len(t)<=4:
        print('  @0x%08X  %r'%(s,t))