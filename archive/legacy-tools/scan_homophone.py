# -*- coding: utf-8 -*-
"""系统扫描「同音/近音替代」型折中译名。
   原理：坏字位的字被替换成形近/同音/形近的另一个字，读起来别扭。"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
P=r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
buf=open(P,'rb').read()
CL=[]
for l in open(r'F:\sr2-cn\_juice_fix\charlist_CH.txt',encoding='utf-8'):
    l=l.strip()
    if not l or l.startswith('//') or l.startswith('#'): continue
    CL.append(int(l))
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '<%04X>'%s

SEG=[(0x1C00000,0x1C80000,'表A'),(0x2E00000,0x2E40000,'表B')]
recs=[]
for lo,hi,name in SEG:
    p=lo
    while p<hi and p+2<=len(buf):
        v=struct.unpack_from('>H',buf,p)[0]
        if v!=0:
            q=p;slots=[]
            while q+2<=len(buf):
                w=struct.unpack_from('>H',buf,q)[0]
                if w==0: break
                slots.append(w); q+=2
            recs.append((p,''.join(dec(s) for s in slots)))
            p=q+2
        else: p+=2

# 8 个历史坏字位 -> 可能被替换成的同音/形近字
BADCH='三会律徒得心必联'
SUBS={
 '律':['李','礼','里','理','力','立','利'],
 '会':['伙','荟','汇','烩','绘'],
 '徒':['途','涂','走','社','如'],
 '得':['德','锝','德'],
 '心':['芯','辛','新'],
 '必':['毕','比','壁','避'],
 '联':['连','莲','联','恋'],
 '三':['散','叁','山'],
}
print('=== 扫描「坏字位同音替代」痕迹 ===')
print()
for bad,subs in SUBS.items():
    hits=[]
    for p,t in recs:
        if bad in t: continue
        for s in subs:
            if s in t and len(t)<=20:
                hits.append((p,s,t)); break
    if hits:
        print('【%s】可能被替代为 %s —— %d 条候选：'%(bad,'/'.join(subs),len(hits)))
        seen=set();n=0
        for p,s,t in hits:
            if t in seen: continue
            seen.add(t)
            # 只打印含替代字的短条目
            print('@0x%08X %r'%(p,t))
            n+=1
            if n>=12: break
        print()
print('='*70)
print('=== 精确列出「法律李」类同音词（最可信）===')
import re
for p,t in recs:
    for m in re.finditer(r'[法律纪律体力礼李里理力立利]',t):
        seg=t[max(0,m.start()-2):m.end()+2]
        if '李' in seg:
            print('  @0x%08X %r'%((p,t)))
            break