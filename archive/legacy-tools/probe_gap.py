# -*- coding: utf-8 -*-
"""测：含「城郊」记录与其后一条记录之间是否有可扩展间隙（gap）"""
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
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '?'
b=open(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc','rb').read()
n=len(b)

# static_CH blob 范围：文件内 base
import struct as st2
base=None
# 用已知锚点：迷雾巷 file 0x01C2D86A = blob 0x61698
base=0x01C2D86A-0x61698
print('static_CH blob base = 0x%08X'%base)
# blob size
SIZE=458880
print('blob 覆盖 [0x%08X, 0x%08X)'%(base,base+SIZE))
print('文件总长 0x%08X  → blob 之后还有 %d 字节'%(n,n-(base+SIZE)))
print()

pat=struct.pack('>2H',S('城'),S('郊'))
hits=[];s=0
while True:
    i=b.find(pat,s)
    if i<0:break
    hits.append(i); s=i+1

def bounds(at):
    p=at
    while p>=2 and struct.unpack_from('>H',b,p-2)[0]!=0: p-=2
    st=p; q=st; o=[]
    while q+2<=n:
        w=struct.unpack_from('>H',b,q)[0]
        if w==0: break
        o.append(w); q+=2
    return st,q+2

info=[]
for i in hits:
    st,en=bounds(i)
    info.append((st,en))
info=sorted(set(info))
print('记录数 =',len(info))
# 检查相邻记录间隙
gaps=[]
for k in range(len(info)-1):
    st,en=info[k]
    nst=info[k+1][0]
    gap=nst-en
    if gap!=0: gaps.append((st,en,nst,gap))
print('相邻记录间隙 != 0 的对数 =',len(gaps))
for st,en,nst,g in gaps[:20]:
    print('   rec@0x%08X end=0x%08X  next@0x%08X  gap=%d  bytes=%s'%(
        st,en,nst,g,b[en:nst].hex(' ')))
print()
# 也检查每条记录后面到下一条是否连续
print('=== 前 12 条记录的原始 slot 尾部 ===')
for st,en in info[:12]:
    o=[]
    q=en-2
    while q>=st:
        o.append(struct.unpack_from('>H',b,q)[0]); q-=2
    o.reverse()
    print('  @0x%08X len=%d tail=%s'%(st,(en-st)//2,[hex(x) for x in o[-4:]]))