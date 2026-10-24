# -*- coding: utf-8 -*-
"""弹药类折中译名回滚（三项全等长）：
   散筒枪(3) -> 霰弹枪(3)
   火料  (2) -> 弹药  (2)
   填料  (2) -> 弹药  (2)
"""
import sys, struct, os, shutil, hashlib
sys.stdout.reconfigure(encoding='utf-8')
GAME=r'G:\SteamLibrary\steamapps\common\Saints Row 2'
PATCH=os.path.join(GAME,'patch.vpp_pc')
BAK=PATCH+'.before_ammo2.bak'
EXPECT_MD5='dabbeee8c3ab49af22946a558f7cfe56'

def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l[0] in '/#': continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
IDX={cp:i for i,cp in enumerate(CL)}
def S(c):
    if ord(c) not in IDX: raise KeyError('%s U+%04X 不在字表'%(c,ord(c)))
    return IDX[ord(c)]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '?'

buf=open(PATCH,'rb').read()
md5=hashlib.md5(buf).hexdigest()
print('当前 md5 =',md5)
assert md5==EXPECT_MD5,'★ 基线不符，拒绝写入'
print('  ✓ 基线正确（= 市郊 改后版本）')
print('  size =',len(buf))
print()

PAIRS=[('散筒枪','霰弹枪',6),('火料','弹药',14),('填料','弹药',1)]
def P(w): return struct.pack('>%dH'%len(w),*[S(c) for c in w])

print('=== 改前计数 ===')
for old,new,exp in PAIRS:
    po,pn=P(old),P(new)
    print('  %-6s=%-3d (期望%d)   %-6s=%-3d'%(old,buf.count(po),exp,new,buf.count(pn)))

out=buf
for old,new,exp in PAIRS:
    po,pn=P(old),P(new)
    c=out.count(po)
    assert c==exp,'★ %s 命中 %d != 期望 %d'%(old,c,exp)
    out=out.replace(po,pn)
    print('  已改 %s -> %s  %d 处'%(old,new,c))

print()
print('=== 改后校验 ===')
ok=True
for old,new,exp in PAIRS:
    c=out.count(P(old))
    print('  %-6s 残留=%d (期望0)'%(old,c))
    if c: ok=False
assert ok
print('  长度不变 =',len(out)==len(buf))
d=sum(1 for x,y in zip(buf,out) if x!=y)
print('  差异字节 =',d,'(期望 = (3+2+2+2+2)*... 按命中数算)')
assert len(out)==len(buf)
print('  弹药 总命中 =',out.count(P('弹药')),'(改前75 + 14 + 1 = 90)')
assert out.count(P('弹药'))==75+14+1

print()
print('=== 解码回读 ===')
n=len(out)
def bounds(at):
    p=at
    while p>=2 and struct.unpack_from('>H',out,p-2)[0]!=0: p-=2
    st=p;q=st;o=[]
    while q+2<=n:
        w=struct.unpack_from('>H',out,q)[0]
        if w==0: break
        o.append(w);q+=2
    return st,q+2,o
for old,new,exp in PAIRS:
    pn=P(new)
    st=0; cnt=0
    while True:
        i=out.find(pn,st)
        if i<0: break
        # 只回读本次改动的那几条：简单起见打印前若干
        if cnt<6:
            s,e,_o3=bounds(i)
            o=[struct.unpack_from('>H',out,s+2*k)[0] for k in range((e-s)//2)][:-1]
            t=''.join(dec(x) for x in o).replace('\n','')
            print('  @0x%08X %s'%(i,t[:52]))
        cnt+=1; st=i+1
    print('  【%s】全表命中 %d'%(new,cnt))

print()
print('=== 旁证复核（不应变化）===')
for w in ['城郊','市郊','主城区','霰弹枪','三街圣徒','兄弟会','三王','指定辩护律师','子弹','火药']:
    print('  %-8s = %d'%(w,out.count(P(w)) if all(ord(c) in IDX for c in w) else 'N/A'))

if not os.path.exists(BAK):
    shutil.copy2(PATCH,BAK); print('\n已备份 ->',BAK)
open(PATCH,'wb').write(out)
print('已写入')
print('新 md5 =',hashlib.md5(open(PATCH,'rb').read()).hexdigest())
print('新 size =',os.path.getsize(PATCH))