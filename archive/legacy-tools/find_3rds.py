# -*- coding: utf-8 -*-
"""查找 3rds 及其现有译名，评估改回「三街圣徒」的可行性"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
PATCH=r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'

def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l.startswith('//') or l.startswith('#'): continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
idx={cp:i for i,cp in enumerate(CL)}
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '<%04X>'%s

buf=open(PATCH,'rb').read()
print('patch = %d 字节'%len(buf))

# 1) ASCII "3rds" 在 le_strings(slot=u16BE ASCII) 中
print()
print('=== 搜索 ASCII "3rds" (u16 BE) ===')
pat=b''.join(struct.pack('>H',ord(c)) for c in '3rds')
hits=[];st=0
while True:
    i=buf.find(pat,st)
    if i<0: break
    hits.append(i); st=i+1
print('命中 %d 处'%len(hits))
for h in hits[:40]:
    # 反推记录起点
    p=h
    while p>=2:
        v=struct.unpack_from('>H',buf,p-2)[0]
        if v==0: break
        p-=2
    start=p
    q=start; out=[]
    while q+2<=len(buf):
        v=struct.unpack_from('>H',buf,q)[0]
        if v==0: break
        out.append(v); q+=2
    txt=''.join(dec(v) for v in out)
    rid=struct.unpack_from('<I',buf,start-4)[0] if start>=4 else 0
    print('  @0x%X len=%d  %r'%(h,len(out),txt))

print()
print('=== 搜索 ASCII "3rd" (单数) ===')
pat3=b''.join(struct.pack('>H',ord(c)) for c in '3rd')
st=0;n=0
while True:
    i=buf.find(pat3,st)
    if i<0: break
    n+=1; st=i+1
print('命中 %d 处'%n)

print()
print('=== 搜索常见中文译名候选 ===')
for cand in ['三街圣徒','三街','第三街','3街','圣徒','三合会']:
    if all(ord(c) in idx for c in cand):
        s=b''.join(struct.pack('>H',idx[ord(c)]+0x20) for c in cand)
        c=buf.count(s)
        print('  %-6r slot序列在 patch 中命中 %d 处  ✓字表全有'%(cand,c))
    else:
        miss=[ch for ch in cand if ord(ch) not in idx]
        print('  %-6r ✗ 字表缺 %s'%(cand,miss))

print()
print('=== 「三街圣徒」逐字 slot ===')
for ch in '三街圣徒':
    cp=ord(ch)
    if cp in idx:
        i=idx[cp]
        flag=''
        if i in (239,348,1057,1058,1059,1065,1066,2100):
            flag='   <<< 已知坏字位 idx=%d'%i
        print('  %s U+%04X idx=%-5d slot=0x%04X%s'%(ch,cp,i,i+0x20,flag))
    else:
        print('  %s U+%04X ✗ 字表缺'%(ch,cp))