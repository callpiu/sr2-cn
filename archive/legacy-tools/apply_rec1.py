# -*- coding: utf-8 -*-
"""REC1: 你的[format][color:green]弟兄们[/format]需要你的保护
   ->  [format][color:green]一众伴[/format]伙临敌急待我救援
   等长替换(slot制)，两条同文记录一起改(同文双记录陷阱)"""
import sys, struct, shutil, os, hashlib
sys.stdout.reconfigure(encoding='utf-8')

GAME=r'G:\SteamLibrary\steamapps\common\Saints Row 2'
PATCH=os.path.join(GAME,'patch.vpp_pc')
BAK=PATCH+'.v535_before_rec1.bak'

def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l.startswith('//') or l.startswith('#'): continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
idx={cp:i for i,cp in enumerate(CL)}
def slot(ch):
    cp=ord(ch)
    assert cp in idx, '字表缺字: %s U+%04X'%(ch,cp)
    return idx[cp]+0x20
def dec(s):
    return chr(CL[s-0x20]) if s>=0x20 and (s-0x20)<len(CL) else '<%04X>'%s

OLD_HDR='你的'
OLD_GRN='弟兄们'
OLD_BODY='需要你的保护'
NEW_GRN='一众伴'
NEW_B1='伙临敌'
NEW_B2='急待我救援'

TAG='[format][color:green]'
POST='[/format]'
OLD_TEXT=OLD_HDR+TAG+OLD_GRN+POST+OLD_BODY
NEW_TEXT=TAG+NEW_GRN+POST+NEW_B1+NEW_B2

print('原文 %d字 = %r'%(len(OLD_TEXT),OLD_TEXT))
print('新文 %d字 = %r'%(len(NEW_TEXT),NEW_TEXT))
assert len(OLD_TEXT)==len(NEW_TEXT), '★ 长度不等，slot制不能改'
old_slots=[slot(c) for c in OLD_TEXT]
new_slots=[slot(c) for c in NEW_TEXT]
print('旧 slots(%d) = %s'%(len(old_slots),' '.join('%04X'%s for s in old_slots)))
print('新 slots(%d) = %s'%(len(new_slots),' '.join('%04X'%s for s in new_slots)))
print()

pat=struct.pack('>%dH'%len(old_slots),*old_slots)
newpat=struct.pack('>%dH'%len(new_slots),*new_slots)

buf=open(PATCH,'rb').read()
orig_md5=hashlib.md5(buf).hexdigest()
print('patch.vpp_pc  %d 字节  md5=%s'%(len(buf),orig_md5))
assert orig_md5=='2fd6a5e9d517971e2135c5a34c6daf68', '★ md5 不等于 v534(2fd6a5e9)，中止！实际=%s'%orig_md5
print('  ✓ 基线确认 = v534')
print()

hits=[];st=0
while True:
    i=buf.find(pat,st)
    if i<0: break
    hits.append(i); st=i+1
print('命中 %d 处' % len(hits))
assert len(hits)==2, '★ 期望 2 处，实际 %d'%len(hits)

out=bytearray(buf)
for h in hits:
    # 前置断言：往前4字节应为记录ID(非0)，往后应为 0000 终止符
    rid=struct.unpack_from('<I',out,h-4)[0]
    tail=struct.unpack_from('>H',out,h+len(old_slots)*2)[0]
    dec_pre=''.join(dec(s) for s in struct.unpack_from('>%dH'%len(old_slots),out,h))
    print('  @0x%X  ID前4B=0x%08X  终止符=0x%04X'%(h,rid,tail))
    print('     现文核对 = %r  %s'%(dec_pre,'✓一致' if dec_pre==OLD_TEXT else '✗不一致'))
    assert dec_pre==OLD_TEXT, '★ 现文与预期不符'
    assert tail==0, '★ 后面不是 0000 终止符'
    assert rid!=0, '★ ID 前4字节为 0，起点可疑'
    out[h:h+len(new_slots)*2]=newpat
    print('     ✓ 已改写')

# 改后立即重读校验
print()
print('=== 改后回读校验 ===')
n=0;st=0
while True:
    i=bytes(out).find(newpat,st)
    if i<0: break
    n+=1; st=i+1
print('新文本模式命中 %d 处 (期望2)'%n)
assert n==2
# 旧模式应归零
m=0;st=0
while True:
    i=bytes(out).find(pat,st)
    if i<0: break
    m+=1; st=i+1
print('旧文本模式残留 %d 处 (期望0)'%m)
assert m==0
print()
print('差异字节总数 =', sum(1 for a,b in zip(buf,out) if a!=b))
print('文件长度不变 =', len(buf)==len(out))
assert len(buf)==len(out)

if not os.path.exists(BAK):
    shutil.copy2(PATCH,BAK)
    print()
    print('已备份 ->',BAK)
open(PATCH,'wb').write(bytes(out))
print('已写入',PATCH)
print('新 md5 =',hashlib.md5(open(PATCH,'rb').read()).hexdigest())