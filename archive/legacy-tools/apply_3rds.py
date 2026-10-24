# -*- coding: utf-8 -*-
"""3rdS -> 三街圣徒 （等长 4 字符替换，两处同文记录一起改）"""
import sys, struct, shutil, os, hashlib
sys.stdout.reconfigure(encoding='utf-8')
GAME=r'G:\SteamLibrary\steamapps\common\Saints Row 2'
PATCH=os.path.join(GAME,'patch.vpp_pc')
BAK=PATCH+'.before_3rds.bak'

def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l.startswith('//') or l.startswith('#'): continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
IDX={cp:i for i,cp in enumerate(CL)}
def slot(ch):
    cp=ord(ch); assert cp in IDX,'字表缺 %s'%ch
    return IDX[cp]+0x20

OLD='3rdS'
NEW='三街圣徒'
print('原文 %r (%d) -> 新文 %r (%d)'%(OLD,len(OLD),NEW,len(NEW)))
assert len(OLD)==len(NEW),'长度不等'
old_slots=[ord(c) for c in OLD]          # ASCII 直接就是 slot 值
new_slots=[slot(c) for c in NEW]
print('旧 slots = %s'%' '.join('%04X'%s for s in old_slots))
print('新 slots = %s   (%s)'%(' '.join('%04X'%s for s in new_slots),
      ' '.join('%s(idx%d)'%(c,IDX[ord(c)]) for c in NEW)))

pat=struct.pack('>4H',*old_slots)
newpat=struct.pack('>4H',*new_slots)

buf=open(PATCH,'rb').read()
md5=hashlib.md5(buf).hexdigest()
print()
print('patch md5 = %s  (%d 字节)'%(md5,len(buf)))
assert md5=='ea23ead48158c85234b8aa876e10a2df','★ md5 不是修复版(ea23ead4)，中止！'
print('  ✓ 基线 = 外部修复版')
print()

hits=[];st=0
while True:
    i=buf.find(pat,st)
    if i<0: break
    hits.append(i); st=i+1
print('ASCII "3rdS" 命中 %d 处'%len(hits))
assert len(hits)==2,'★ 期望2处，实际 %d'%len(hits)

out=bytearray(buf)
for h in hits:
    # 前缀应是 7304 657A（记录ID的一部分）
    pre=struct.unpack_from('>2H',out,h-4)
    tail=struct.unpack_from('>H',out,h+8)[0]
    print('  @0x%X  前4字节=%04X %04X  后终止符=0x%04X'%(h,pre[0],pre[1],tail))
    assert pre==(0x7304,0x657A),'★ 前缀不符，中止'
    assert tail==0,'★ 后面不是 0000 终止符'
    cur=''.join(chr(v) for v in struct.unpack_from('>4H',out,h))
    print('     现文核对 = %r  %s'%(cur,'✓' if cur==OLD else '✗'))
    assert cur==OLD
    out[h:h+8]=newpat
    print('     ✓ 已改写为「%s」'%NEW)

print()
print('=== 改后回读 ===')
b=bytes(out)
# 基线里本就有 104 处「三街圣徒」+ 改的 2 处 = 106
base=buf.count(newpat)
print('  基线原有「三街圣徒」 = %d 处'%base)
print('  ASCII "3rdS" 残留 = %d (期望0)'%b.count(pat))
assert b.count(pat)==0
print('  改后「三街圣徒」 = %d 处 (期望 %d)'%(b.count(newpat),base+2))
assert b.count(newpat)==base+2
print('  长度不变 = %s'%(len(b)==len(buf)))
print('  差异字节 = %d'%sum(1 for x,y in zip(buf,b) if x!=y))
assert len(b)==len(buf)

if not os.path.exists(BAK):
    shutil.copy2(PATCH,BAK); print('\n已备份 ->',BAK)
open(PATCH,'wb').write(b)
print('已写入 patch.vpp_pc')
print('新 md5 =',hashlib.md5(open(PATCH,'rb').read()).hexdigest())