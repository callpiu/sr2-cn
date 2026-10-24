# -*- coding: utf-8 -*-
"""按位置区间判断归属：已知 static_CH 中文记录 @0x1C6AE16 / @0x2E0CBF0"""
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

# 已知中文基准点
CN=['0x1C6AE16','0x2E0CBF0']
print('=== 已知中文(static_CH)基准点 ===')
pat=b''.join(struct.pack('>H',IDX[ord(c)]+0x20) for c in '需要你的保护')
st=0
while True:
    i=buf.find(pat,st)
    if i<0: break
    print('   @0x%08X'%i); st=i+1

print()
print('=== 3rdS / 3rd Street 1 / 3rd Street 2 的位置 ===')
for probe in ['3rdS','3rd Street 1','3rd Street 2']:
    pb=b''.join(struct.pack('>H',ord(c)) for c in probe)
    st=0
    while True:
        i=buf.find(pb,st)
        if i<0: break
        p=rec_start(i)
        slots=txt_at(p)
        t=''.join(dec(s) for s in slots)
        has_cn=any('\u4e00'<=c<='\u9fff' for c in t)
        print('   %-14s @0x%08X 起点=%d %2d字 %s'%(repr(probe),i,p,len(slots),repr(t)))
        st=i+1

print()
print('=== 判断：0x1C2E244 附近的邻居是什么语种 ===')
# 取 0x1C2E000..0x1C2E800 的所有记录，看语种分布
p=0x1C2E100
cnt_ascii=cnt_cn=cnt_de=0
samples=[]
while p<0x1C2E900:
    if p+2>len(buf): break
    if struct.unpack_from('>H',buf,p)[0]==0:
        p+=2; continue
    slots=txt_at(p)
    if not slots: break
    t=''.join(dec(s) for s in slots)
    L=len(t)
    if L>3:
        iscn=sum(1 for c in t if '\u4e00'<=c<='\u9fff')
        isde=sum(1 for c in t if c in'äöüßÄÖÜ')
        if iscn>=2: cnt_cn+=1
        elif isde>=2: cnt_de+=1
        elif all(ord(c)<128 for c in t if c.isprintable()): cnt_ascii+=1
        if len(samples)<12 and 0x1C2E200<=p<=0x1C2E400:
            samples.append((p,t[:40]))
    p+=2*(len(slots)+1)
print('   该区间: 中文记录=%d 德文记录=%d 纯ASCII记录=%d'%(cnt_cn,cnt_de,cnt_ascii))
for s in samples: print('     @0x%X %r'%s)