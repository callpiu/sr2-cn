# -*- coding: utf-8 -*-
"""列出历史上因坏字位而绕行的高可信候选。
   判据（按可信度排序）：
   A. 曾用 ASCII 代替中文的（3rdS 这种）—— 已找完，0残留
   B. 用词明显不通、像是为避开某字而选的替代词
   C. 与官方英文原文对照可发现该用某字、却用了别的字
   """
import sys, struct, os
sys.stdout.reconfigure(encoding='utf-8')
P=r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
buf=open(P,'rb').read()
CL=[]
for l in open(r'F:\sr2-cn\_juice_fix\charlist_CH.txt',encoding='utf-8'):
    l=l.strip()
    if not l or l.startswith('//') or l.startswith('#'): continue
    CL.append(int(l))
IDX={cp:i for i,cp in enumerate(CL)}
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '<%04X>'%s

SEG=[(0x1C00000,0x1C80000,'表A'),(0x2E00000,0x2E40000,'表B')]
recs=[]
for lo,hi,name in SEG:
    p=lo
    while p<hi and p+2<=len(buf):
        v=struct.unpack_from('>H',buf,p)[0]
        if v!=0:
            q=p;slots=[]
            while q+2<=len(buf):
                w=struct.unpack_from('>H',buf,q)[0]
                if w==0: break
                slots.append(w); q+=2
            recs.append((p,name,''.join(dec(s) for s in slots)))
            p=q+2
        else: p+=2

# ============ 已知历史折中（来自记忆台账）============
# 1) 斯蒂尔沃特大学学生会（会→伙 撞车）
# 2) 三街圣徒 3rdS（已回滚）
# 3) 各处因"律/徒/心/必/得/三"坏字位而改的词
KNOWN=[
 ('学生会','斯蒂尔沃特大学学生会'),
 ('大学学生会','大学学生会'),
]
print('=== A. 学生会系列（当年因「会」坏字位改过）===')
for kw in ['学生会','大学学生会','学生联']:
    hits=[(p,n,t) for p,n,t in recs if kw in t]
    print('  关键词 %r 命中 %d 条'%(kw,len(hits)))
    for p,n,t in hits:
        print('     @0x%08X %r'%(p,t))
print()

print('=== B. 含「伙」的条目（「会」被替成伙的痕迹）===')
h=[(p,n,t) for p,n,t in recs if '伙' in t and len(t)<=16]
for p,n,t in h: print('  @0x%08X %r'%(p,t))
print()

print('=== C. 圣徒系列短条目（徒 是坏字位，核对是否还有折中）===')
h=[(p,n,t) for p,n,t in recs if '圣徒' in t and len(t)<=10]
seen=set()
for p,n,t in h:
    if t in seen: continue
    seen.add(t)
    print('  @0x%08X %r'%(p,t))
print()

print('=== D. 法律/律 相关（「律」坏字位）===')
h=[(p,n,t) for p,n,t in recs if '律' in t and len(t)<=16]
seen=set()
for p,n,t in h:
    if t in seen: continue
    seen.add(t); print('  @0x%08X %r'%(p,t))
print()

print('=== E. 「得」被替词的痕迹：搜常见别扭表达 ===')
for kw in ['显得','获得','觉得','懂得','使得','不得不','得以']:
    hits=[(p,t) for p,n,t in recs if kw in t]
    print('  %-6s %d 条  例:%s'%(kw,len(hits),hits[0][1][:40] if hits else '-'))
print()

print('=== F. 「必」相关：搜「必须」是否完整 ===')
h=[(p,t) for p,n,t in recs if '必须' in t]
print('  含「必须」%d 条（首条: %s）'%(len(h),h[0][1][:36] if h else '-'))
print()

print('=== G. 「心」相关：搜「担心/放心」等 ===')
h=[(p,t) for p,n,t in recs if '心' in t and len(t)<=14]
seen=set()
n=0
for p,t in h:
    if t in seen: continue
    seen.add(t); print('  @0x%08X %r'%(p,t)); n+=1
    if n>15: break
print()
print('总记录 %d'%len(recs))