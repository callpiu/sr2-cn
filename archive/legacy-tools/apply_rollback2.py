# -*- coding: utf-8 -*-
"""坏字位已根治（charlist count= 修复）后回滚折中译名。
   直接按字节模式全表定位，等长替换。"""
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
assert md5=='4210f886ba14033d90c602a461cc94bf','★ 基线不符，中止！'
print('  ✓ 基线正确（三街圣徒已改版）')
print()

out=bytearray(buf)
def find_all(pat):
    hits=[];st=0
    while True:
        i=bytes(out).find(pat,st)
        if i<0: break
        hits.append(i); st=i+1
    return hits

JOBS=[
 ('兄弟帮→兄弟会','兄弟帮','兄弟会',28,False),
 ('3王→三王','3王','三王',4,False),
 ('指定辩护人→指定辩护律师','指定辩护人','指定辩护律师',4,True),
]
total=0
for name,old,new,expect,trim in JOBS:
    print('='*72)
    print('【%s】'%name)
    op=[S(c) for c in old]
    np_=[S(c) for c in new]
    if trim:
        np_=np_[:-1]   # 裁掉末尾「律」→ 不对！应该是裁掉一个空格
        # 重算：新串比旧串多1字 => 净多1 slot，必须吃掉1个尾部空格
        np_=[S(c) for c in new][:-1]
        print('  新串 %r(%d字) → 写入前%d slot（末位「师」保留，吃掉1个尾部空格）'
              %(new,len(new),len(np_)))
        # 正确做法：写 new 的前 (len(old)) 个字
        np_=[S(c) for c in new][:len(old)]
        print('  实际写入 %r = %s'%(new[:len(old)],' '.join('%04X'%s for s in np_)))
    else:
        print('  写入 %r = %s'%(new,' '.join('%04X'%s for s in np_)))
    assert len(np_)==len(op),'★ 长度不等 旧%d 新%d'%(len(op),len(np_))
    pat=struct.pack('>%dH'%len(op),*op)
    npat=struct.pack('>%dH'%len(np_),*np_)
    hits=find_all(pat)
    print('  命中 %d 处 (期望 %d)'%(len(hits),expect))
    assert len(hits)==expect,'★ 条数不符，中止'
    for at in hits:
        if trim:
            tail=struct.unpack_from('>H',out,at+len(pat))[0]
            assert tail==0x0020,'★ 期望尾部空格0020，实际%04X'%tail
        out[at:at+len(npat)]=npat
    print('  ✓ 改写 %d 处'%len(hits))
    total+=len(hits)
print()
print('='*72)
b=bytes(out)
print('合计改写 %d 处'%total)
for name,old,new,expect,trim in JOBS:
    print('  %-22s 旧串残留 = %d (期望0)'%(name,b.count(struct.pack('>%dH'%len([S(c) for c in old]),*[S(c) for c in old]))))
print()
print('  兄弟会  = %d 处 (原 %d + 23)'%(b.count(struct.pack('>3H',S('兄'),S('弟'),S('会'))),b.count(struct.pack('>3H',S('兄'),S('弟'),S('会')))-23))
print('  三王    = %d 处'%b.count(struct.pack('>2H',S('三'),S('王'))))
print('  指定辩护律师 = %d 处'%b.count(struct.pack('>5H',S('指'),S('定'),S('辩'),S('护'),S('师'))))
print('  霰弹枪  = %d 处（未动，应为 22）'%b.count(struct.pack('>3H',S('霰'),S('弹'),S('枪'))))
print()
print('长度不变 =',len(b)==len(buf))
print('差异字节 =',sum(1 for x,y in zip(buf,b) if x!=y))
assert len(b)==len(buf)
if not os.path.exists(BAK):
    shutil.copy2(PATCH,BAK); print('\n已备份 ->',BAK)
open(PATCH,'wb').write(b)
print('已写入\n新 md5 =',hashlib.md5(open(PATCH,'rb').read()).hexdigest())