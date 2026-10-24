# -*- coding: utf-8 -*-
"""深挖那条 '3rdS' 记录 + 找所有疑似未汉化的 gang 名残留"""
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
IDX={cp:i for i,cp in enumerate(CL)}
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '<%04X>'%s
buf=open(PATCH,'rb').read()

def rec_at_text(text_start):
    q=text_start; out=[]
    while q+2<=len(buf):
        v=struct.unpack_from('>H',buf,q)[0]
        if v==0: break
        out.append(v); q+=2
    return out,q

def hash_of(off):
    id1=struct.unpack_from('<H',buf,off-4)[0]
    id2=struct.unpack_from('<H',buf,off-2)[0]
    return (id1<<16)|id2

print('=== 1) 那条 "3rdS" 记录详情 ===')
pat=b''.join(struct.pack('>H',ord(c)) for c in '3rdS')
st=0
while True:
    i=buf.find(pat,st)
    if i<0: break
    p=i
    while p>=2:
        if struct.unpack_from('>H',buf,p-2)[0]==0: break
        p-=2
    slots,q=rec_at_text(p)
    h=hash_of(p)
    print('  文本@0x%X  hash=0x%08X  长度=%d字'%(p,h,len(slots)))
    print('  原文=%r'%''.join(dec(s) for s in slots))
    print('  slot序列=%s'%' '.join('%04X'%s for s in slots))
    print()
    st=i+1

print('=== 2) 所有含 ASCII 的 gang 名残留（中文表中）===')
# 找形如 "3rd Street 1" / "3rdS" / "3rd Street Saints" 这类
for probe in ['3rdS','3rd Street 1','3rd Street 2','3rd Street']:
    pb=b''.join(struct.pack('>H',ord(c)) for c in probe)
    st=0;res=[]
    while True:
        i=buf.find(pb,st)
        if i<0: break
        p=i
        while p>=2:
            if struct.unpack_from('>H',buf,p-2)[0]==0: break
            p-=2
        slots,q=rec_at_text(p)
        txt=''.join(dec(s) for s in slots)
        res.append((i,hash_of(p),len(slots),txt))
        st=i+1
    print('  %-14r 命中 %d 条'%(probe,len(res)))
    for i,h,L,t in res:
        print('      @0x%X hash=0x%08X %d字 %r'%(i,h,L,t))

print()
print('=== 3) 「三街圣徒」各条长度分布（找等长可替换的）===')
pat=b''.join(struct.pack('>H',IDX[ord(c)]+0x20) for c in '三街圣徒')
from collections import Counter
c=Counter();st=0
recs=[]
while True:
    i=buf.find(pat,st)
    if i<0: break
    p=i
    while p>=2:
        if struct.unpack_from('>H',buf,p-2)[0]==0: break
        p-=2
    slots,q=rec_at_text(p)
    txt=''.join(dec(s) for s in slots)
    recs.append((p,hash_of(p),len(slots),txt))
    st=i+1
print('  共 %d 条'%len(recs))
print('  按hash 分组(同hash=同一条记录的多语种副本):')
byh=Counter(h for _,h,_,_ in recs)
for h,cnt in byh.most_common():
    print('     hash 0x%08X  中文出现 %d 次'%(h,cnt))
print()
print('  完整短条目(≤12字，便于核对):')
for p,h,L,t in recs:
    if L<=12:
        print('     hash 0x%08X %2d字 %r'%(h,L,t))