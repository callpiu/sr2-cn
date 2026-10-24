# -*- coding: utf-8 -*-
"""定位 3rdS / 3rd Street 1 / 3rd Street 2 所属的表，判断游戏是否会读它"""
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

def rec_start(i):
    p=i
    while p>=2:
        if struct.unpack_from('>H',buf,p-2)[0]==0: break
        p-=2
    return p
def txt_at(t):
    q=t;out=[]
    while q+2<=len(buf):
        v=struct.unpack_from('>H',buf,q)[0]
        if v==0: break
        out.append(v); q+=2
    return out

# 找所有 le_strings 表头：A84C7F73 magic
print('=== 定位所有 le_strings 表（magic A84C7F73）===')
MAG=b'\xa7\x4c\xa8\x73'   # LE of A84C7F73
st=0;tabs=[]
while True:
    i=buf.find(MAG,st)
    if i<0: break
    tabs.append(i); st=i+1
print('找到 %d 个表头:'%len(tabs))
for t in tabs:
    # 头后 0x40C 起是指针数组
    print('  @0x%08X'%t)
print()

def which_tab(off):
    best=None
    for t in tabs:
        if t<=off: best=t
    return best

print('=== 3rdS 等条目落在哪个表区间 ===')
targets={}
for probe in ['3rdS','3rd Street 1','3rd Street 2']:
    pb=b''.join(struct.pack('>H',ord(c)) for c in probe)
    st=0
    while True:
        i=buf.find(pb,st)
        if i<0: break
        targets.setdefault(probe,[]).append(i); st=i+1

for probe,locs in targets.items():
    print()
    print('  %r:'%probe)
    # 找最近的表头
    for i in locs:
        tb=which_tab(i)
        rel = i-tb if tb is not None else None
        print('     @0x%08X  最近表头=0x%08X  区内偏移=%s'%(i,tb,('0x%X'%rel) if rel is not None else 'N/A'))

print()
print('=== 关键：中文表里"三街圣徒"104 条分别落在哪个表 ===')
pat=b''.join(struct.pack('>H',IDX[ord(c)]+0x20) for c in '三街圣徒')
st=0;from collections import Counter
c=Counter()
while True:
    i=buf.find(pat,st)
    if i<0: break
    tb=which_tab(i)
    c[('0x%08X'%tb) if tb is not None else 'none']+=1
    st=i+1
for k,v in c.most_common():
    print('   表 %s : %d 条'%(k,v))
print()
print('=== 对比：3rdS 所在表 vs 三街圣徒所在表 ===')