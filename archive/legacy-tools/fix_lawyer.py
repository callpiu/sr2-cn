# -*- coding: utf-8 -*-
"""修「指定辩护律」→ 「指定辩护律师」
   尾部都有空格 slot，用「师」替换第一个空格，长度不变。"""
import sys, struct, shutil, os, hashlib
sys.stdout.reconfigure(encoding='utf-8')
GAME=r'G:\SteamLibrary\steamapps\common\Saints Row 2'
PATCH=os.path.join(GAME,'patch.vpp_pc')
BAK=PATCH+'.before_lawefix.bak'
def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l.startswith('//') or l.startswith('#'): continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
IDX={cp:i for i,cp in enumerate(CL)}
def S(ch): return IDX[ord(ch)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '<%04X>'%s

buf=open(PATCH,'rb').read()
md5=hashlib.md5(buf).hexdigest()
print('md5 = %s'%md5)
assert md5=='5a9832960247d1f53f260b25e7bab1a2','★ 基线不符'
print('  ✓ 基线 = 回滚后版本')
print()

oldpat=struct.pack('>6H',S('指'),S('定'),S('辩'),S('护'),S('律'),0x0020)
newpat=struct.pack('>6H',S('指'),S('定'),S('辩'),S('护'),S('律'),S('师'))
hits=[];st=0
b=buf
while True:
    i=b.find(oldpat,st)
    if i<0: break
    hits.append(i); st=i+1
print('「指定辩护律+空格」命中 %d 处 (期望4)'%len(hits))
assert len(hits)==4,'★ 条数不符'

out=bytearray(buf)
for at in hits:
    out[at:at+12]=newpat
    print('  @0x%08X 已改' % at)

b2=bytes(out)
print()
print('=== 校验 ===')
print('  「指定辩护人」残留 = %d (期望0)'%b2.count(struct.pack('>5H',S('指'),S('定'),S('辩'),S('护'),S('人'))))
print('  「指定辩护律 」残留 = %d (期望0)'%b2.count(oldpat))
print('  「指定辩护律师」= %d 处 (期望4)'%b2.count(newpat))
print('  长度不变 =',len(b2)==len(buf))
print('  差异字节 =',sum(1 for x,y in zip(buf,b2) if x!=y))
assert len(b2)==len(buf) and b2.count(newpat)==4

# 独立解码回读
print()
print('=== 解码回读 ===')
st=0
pat=struct.pack('>6H',S('指'),S('定'),S('辩'),S('护'),S('律'),S('师'))
while True:
    i=b2.find(pat,st)
    if i<0: break
    p=i
    while p>=2:
        if struct.unpack_from('>H',b2,p-2)[0]==0: break
        p-=2
    q=p;o=[]
    while q+2<=len(b2):
        w=struct.unpack_from('>H',b2,q)[0]
        if w==0: break
        o.append(w); q+=2
    print('  @0x%08X %r'%(i,''.join(dec(x) for x in o)))
    st=i+1

if not os.path.exists(BAK):
    shutil.copy2(PATCH,BAK); print('\n已备份 ->',BAK)
open(PATCH,'wb').write(b2)
print('已写入\n新 md5 =',hashlib.md5(open(PATCH,'rb').read()).hexdigest())