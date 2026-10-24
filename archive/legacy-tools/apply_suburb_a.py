# -*- coding: utf-8 -*-
"""方案A：Suburbs「城郊」→「市郊」，32 处等长替换
   等长 2字->2字，只动 slot，不碰桶指针，长度不变"""
import sys, struct, os, shutil, hashlib
sys.stdout.reconfigure(encoding='utf-8')
GAME=r'G:\SteamLibrary\steamapps\common\Saints Row 2'
PATCH=os.path.join(GAME,'patch.vpp_pc')
BAK=PATCH+'.before_suburb.bak'
EXPECT_MD5='ebc4de9963af78cae2292c7ffaf7da7b'

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

print('slot: 城=0x%04X 郊=0x%04X → 市=0x%04X 郊=0x%04X'%(S('城'),S('郊'),S('市'),S('郊')))
buf=open(PATCH,'rb').read()
md5=hashlib.md5(buf).hexdigest()
print('当前 md5 =',md5)
assert md5==EXPECT_MD5,'★ 基线不符，拒绝写入'
print('  ✓ 基线正确（= 指定辩护律师 修复后版本）')
print('  size =',len(buf))
print()

OLD=struct.pack('>2H',S('城'),S('郊'))
NEW=struct.pack('>2H',S('市'),S('郊'))
print('「城郊」原始命中 =',buf.count(OLD),'(期望32)')
print('「市郊」现有命中 =',buf.count(NEW),'(期望0)')

# 全文件替换（等长，直接整体 count 校验）
n1=buf.count(OLD)
n2=buf.count(NEW)
out=buf.replace(OLD,NEW)
m1=out.count(OLD); m2=out.count(NEW)
print()
print('=== 替换后校验 ===')
print('  「城郊」残留 = %d (期望0)'%m1)
print('  「市郊」命中 = %d (期望 %d = 原0 + 改%d)'%(m2,n2+n1,n1))
assert m1==0 and m2==n1, '★ 计数异常'
print('  长度不变 =',len(out)==len(buf))
print('  差异字节 =',sum(1 for x,y in zip(buf,out) if x!=y),'(期望64 = 32处×2字)')
assert len(out)==len(buf)
d=sum(1 for x,y in zip(buf,out) if x!=y)
assert d==64, '★ 差异字节数异常: %d'%d

# 回读：解码验证每处上下文
print()
print('=== 改后解码回读（前 12 处）===')
st=0; cnt=0
while True:
    i=out.find(NEW,st)
    if i<0: break
    cnt+=1
    if cnt<=12:
        p=i
        while p>=2 and struct.unpack_from('>H',out,p-2)[0]!=0: p-=2
        o=[];q=p
        while q+2<=len(out):
            w=struct.unpack_from('>H',out,q)[0]
            if w==0: break
            o.append(w); q+=2
        print('  @0x%08X %s'%(i,''.join(dec(x) for x in o).replace('\n','')[:56]))
    st=i+1
print('  共回读 %d 处'%cnt)

# 其他地名未被破坏的复核
print()
print('=== 旁证复核（应与改前一致）===')
for w in ['主城区','城区','城郊','市郊','郊区','三街圣徒','兄弟会','三王','指定辩护律师','霰弹枪']:
    if w in ('城郊','郊区'):
        continue
    p=struct.pack('>%dH'%len(w),*[S(c) for c in w])
    print('  %-8s = %d'%(w,out.count(p)))

if not os.path.exists(BAK):
    shutil.copy2(PATCH,BAK); print('\n已备份 ->',BAK)
else:
    print('\n备份已存在，跳过:',BAK)
open(PATCH,'wb').write(out)
print('已写入')
print('新 md5 =',hashlib.md5(open(PATCH,'rb').read()).hexdigest())
print('新 size =',os.path.getsize(PATCH))