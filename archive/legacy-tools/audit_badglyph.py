# -*- coding: utf-8 -*-
"""坏字位已根治（count= 修复）后，盘点可回滚的折中译名。
   方法：把 8 个「坏字位」slot 所在的所有记录列出来，
        找出当初为绕开坏字位而改写过的条目。"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
P=r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
buf=open(P,'rb').read()
CL=[]
for l in open(r'F:\sr2-cn\_juice_fix\charlist_CH.txt',encoding='utf-8'):
    l=l.strip()
    if not l or l.startswith('//') or l.startswith('#'): continue
    CL.append(int(l))
IDX={cp:i for i,cp in enumerate(CL)}
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '<%04X>'%s

# 8 个历史「坏字位」：idx -> 该位置本应显示的字
BAD={239:'三',348:'会',1057:'律',1058:'徒',1059:'得',1065:'心',1066:'必',2100:'联'}
BADSLOT={i+0x20 for i in BAD}

SEGMENTS=[(0x1C00000,0x1C80000,'表A'),(0x2E00000,0x2E40000,'表B')]
recs=[]
for lo,hi,name in SEGMENTS:
    p=lo
    while p<hi and p+2<=len(buf):
        v=struct.unpack_from('>H',buf,p)[0]
        if v!=0:
            q=p;slots=[]
            while q+2<=len(buf):
                w=struct.unpack_from('>H',buf,q)[0]
                if w==0: break
                slots.append(w); q+=2
            recs.append((p,name,slots))
            p=q+2
        else: p+=2

print('扫描到记录 %d 条'%len(recs))
print()

# 找用到坏字位 slot 的记录
hits=[(p,name,slots) for p,name,slots in recs if BADSLOT & set(slots)]
print('=== 用到 8 个历史坏字位 slot 的记录：%d 条 ==='%len(hits))
for p,name,slots in hits:
    t=''.join(dec(s) for s in slots)
    used=[s for s in slots if s in BADSLOT]
    chars=[BAD[s-0x20] for s in used]
    print('  @0x%08X [%s] %r'%(p,name,t))
    print('        含历史坏字位字: %s'%''.join(chars))
print()

# ★ 关键：查找「同 hash 的其他语种版本」，用于判断这些位置该译成什么
print('=== 找可疑的折中译名（含坏字位字 且 该字全表高频出现）===')
from collections import Counter
allcnt=Counter()
for p,name,slots in recs:
    for s in slots:
        if 0x20<=s<0x20+len(CL): allcnt[CL[s-0x20]]+=1
print('  8 个字在全表的实际使用次数：')
for i,ch in sorted(BAD.items()):
    print('     %s (idx%d) 出现 %d 次'%(ch,i,allcnt.get(ord(ch),0)))
print()

# 找含「圣徒」的记录 —— 三街圣徒/圣徒 关联
print('=== 含「圣徒」的短记录（gang 名相关）===')
for p,name,slots in recs:
    t=''.join(dec(s) for s in slots)
    if '圣徒' in t and len(t)<=12:
        used=[s for s in slots if s in BADSLOT]
        mark='  <<含坏字位 %s'%''.join(BAD[s-0x20] for s in used) if used else ''
        print('  @0x%08X %2d字 %r%s'%(p,len(slots),t,mark))
print()

# 找含「联」的记录（斯蒂尔沃特大学学生会）
print('=== 含「联」的短记录 ===')
for p,name,slots in recs:
    t=''.join(dec(s) for s in slots)
    if '联' in t and len(t)<=14:
        used=[s for s in slots if s in BADSLOT]
        mark='  <<含坏字位' if used else ''
        print('  @0x%08X %2d字 %r%s'%(p,len(slots),t,mark))