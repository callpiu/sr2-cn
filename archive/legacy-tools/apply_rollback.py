# -*- coding: utf-8 -*-
"""坏字位已根治（charlist count= 修复）后回滚折中译名。
   1) 兄弟帮 -> 兄弟会        23 处，等长
   2) 指定辩护人 -> 指定辩护律师   2 处，末尾空格吸收多出的「律」
   3) 3王 -> 三王             3 处，等长
   （霰弹枪 已是正确译名，无需改）"""
import sys, struct, shutil, os, hashlib
sys.stdout.reconfigure(encoding='utf-8')
GAME=r'G:\SteamLibrary\steamapps\common\Saints Row 2'
PATCH=os.path.join(GAME,'patch.vpp_pc')
BAK=PATCH+'.before_rollback.bak'
def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l.startswith('//') or l.startswith('#'): continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
IDX={cp:i for i,cp in enumerate(CL)}
def S(ch):
    cp=ord(ch); assert cp in IDX,'字表缺 %s'%ch; return IDX[cp]+0x20
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '<%04X>'%s

buf=open(PATCH,'rb').read()
md5=hashlib.md5(buf).hexdigest()
print('patch md5 = %s  (%d 字节)'%(md5,len(buf)))
assert md5=='4210f886ba14033d90c602a461cc94bf','★ 基线不符（应为 4210f886 = 三街圣徒已改版），中止！'
print('  ✓ 基线正确')
print()

SEG=[(0x1C00000,0x1C80000),(0x2E00000,0x2E40000)]
def collect():
    out=[]
    for lo,hi in SEG:
        p=lo
        while p<hi and p+2<=len(buf):
            v=struct.unpack_from('>H',buf,p)[0]
            if v!=0:
                q=p;sl=[]
                while q+2<=len(buf):
                    w=struct.unpack_from('>H',buf,q)[0]
                    if w==0: break
                    sl.append(w); q+=2
                out.append((p,sl))
                p=q+2
            else: p+=2
    return out
RECS=collect()
print('扫描 %d 条记录'%len(RECS))
print()

JOBS=[
 # (名称, 旧串, 新串, 期望条数, 新串是否已含[需按尾部空格裁剪])
 ('兄弟帮→兄弟会','兄弟帮','兄弟会',23,False),
 ('3王→三王','3王','三王',3,False),
 ('指定辩护人→指定辩护律师','指定辩护人','指定辩护律师',2,True),
]

out=bytearray(buf)
total=0
for name,old,new,expect,trim in JOBS:
    print('='*70)
    print('【%s】'%name)
    oslots=[S(c) for c in old]
    print('  旧 %r -> %s'%(old,' '.join('%04X'%s for s in oslots)))
    hits=[(p,sl) for p,sl in RECS if ''.join(dec(x) for x in sl).find(old)>=0]
    print('  命中 %d 条 (期望 %d)'%(len(hits),expect))
    assert len(hits)==expect,'★ 条数不符，中止'
    nslots=[S(c) for c in new]
    if trim:
        # 吃掉一个尾部空格
        nslots=nslots[:-1]
        print('  新（裁掉尾部1空格）%s'%' '.join('%04X'%s for s in nslots))
    assert len(nslots)==len(oslots),'★ 长度不等：旧%d 新%d'%(len(oslots),len(nslots))
    print('  等长校验 OK (%d slot)'%len(nslots))
    pat=struct.pack('>%dH'%len(oslots),*oslots)
    npat=struct.pack('>%dH'%len(nslots),*nslots)
    cnt=0
    for p,sl in hits:
        t=''.join(dec(x) for x in sl)
        assert old in t,'★ 记录不含目标串'
        # 在该记录内定位 old 的位置
        tsl=[dec(x) for x in sl]
        for k in range(len(tsl)-len(oslots)+1):
            if tsl[k:k+len(oslots)]==list(old):
                at=p+k*2
                assert bytes(out[at:at+len(pat)])==pat,'★ 槽位字节不符'
                # 尾部空格断言（trim 时）
                if trim:
                    tail=struct.unpack_from('>H',out,at+len(pat))[0]
                    assert tail==0x0020,'★ 期望尾部是空格(0020)，实际 %04X'%tail
                out[at:at+len(npat)]=npat
                cnt+=1
                print('     @0x%08X  %r -> %r'%(at,t[:40],(t[:k]+new+trim*' '+t[k+len(old):])[:40]))
                break
    assert cnt==expect,'★ 实际改写 %d 条'%cnt
    print('  ✓ 改写 %d 条'%cnt)
    total+=cnt
    RECS=[(p,sl) for p,sl in collect()]  # 重新扫描
print()
print('='*70)
print('合计改写 %d 条'%total)
b=bytes(out)
print('旧模式残留检查:')
for name,old,new,expect,trim in JOBS:
    nslots=[S(c) for c in old]
    print('   %-16s 残留 %d (期望0)'%(name,b.count(struct.pack('>%dH'%len(nslots),*nslots))))
print('长度不变 =',len(b)==len(buf))
print('差异字节 =',sum(1 for x,y in zip(buf,b) if x!=y))
assert len(b)==len(buf)

if not os.path.exists(BAK):
    shutil.copy2(PATCH,BAK); print('\n已备份 ->',BAK)
open(PATCH,'wb').write(b)
print('已写入')
print('新 md5 =',hashlib.md5(open(PATCH,'rb').read()).hexdigest())