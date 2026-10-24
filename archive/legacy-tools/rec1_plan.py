import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l.startswith('//') or l.startswith('#'): continue
        xs.append(int(l))
    return xs
CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
idx={cp:i for i,cp in enumerate(CL)}
BAD={1057,239,1066,1058,1065,1059,2100,348}

# REC1 原结构
PRE='你的'
TAG='[format][color:green]'
GREEN='弟兄们'
POSTTAG='[/format]'
BODY='需要你的保护'
print('REC1 原结构:')
print('  黑字段1 %r (%d字)'%(PRE,len(PRE)))
print('  标签    %r (%d字)'%(TAG,len(TAG)))
print('  绿字段  %r (%d字)'%(GREEN,len(GREEN)))
print('  标签    %r (%d字)'%(POSTTAG,len(POSTTAG)))
print('  黑字段2 %r (%d字)'%(BODY,len(BODY)))
tot=len(PRE)+len(TAG)+len(GREEN)+len(POSTTAG)+len(BODY)
print('  合计 %d 字(记录长度必须不变)'%tot)
print()
print('可用净汉字位数 = 11 (等于原句字数)  → 绿字段固定 3 字，黑1+黑2 = 8 字')
print()

CANDS=[
 ('一众伙伴临敌急待我救援', ['一众伴','伙临敌急待我救援']),
 ('一众伙伴临敌急待我支援', ['一众伴','伙临敌急待我支援']),
 ('一众伙伴遭袭急待我救援', ['一众伴','伙遭袭急待我救援']),
 ('一众伙伴遇敌急待我救援', ['一众伴','伙遇敌急待我救援']),
 ('同袍伙伴临敌急待我救援', ['同袍伙','伴临敌急待我救援']),
 ('一众兄弟临敌急待我救援', ['一众兄','弟临敌急待我救援']),
]
print('%-22s %-6s %-18s %s'%('整句','字数','绿字段(3字)','检查'))
print('-'*70)
for whole,(g,b) in CANDS:
    ok = len(whole)==11 and len(g)==3 and (len(g)+len(b))==11
    miss=[ch for ch in whole if ord(ch) not in idx]
    bad=[ch for ch in whole if ord(ch) in idx and idx[ord(ch)] in BAD]
    v='✓' if (ok and not miss and not bad) else '✗'
    print('%-22s %-6d %-18s %s 缺字=%s 坏字位=%s'%(whole,len(whole),g,v,miss or '无',bad or '无'))
print()

NEW='一众伙伴临敌急待我救援'
GREENNEW='一众伴'
B1='伙临敌'
B2='急待我救援'
print('=== 选定方案: %r ==='%NEW)
print('  绿字段3字 %r'%GREENNEW)
print('  黑1  %r (%d)'%(B1,len(B1)))
print('  黑2  %r (%d)'%(B2,len(B2)))
newtxt=PRE+TAG+GREENNEW+POSTTAG+B1+B2
print('  新全文(%d字) = %r'%(len(newtxt),newtxt))
print('  与原文等长? %s'%(len(newtxt)==tot))
miss=[ch for ch in newtxt if ord(ch) not in idx]
print('  全部字在表? %s   缺失=%s'%(not miss,miss or '无'))
# slot
def s(ch): return idx[ord(ch)]+0x20
print()
print('新 slot 序列 =')
print('  绿字段 %r -> %s'%(GREENNEW,[hex(s(c)) for c in GREENNEW]))
print('  黑1    %r -> %s'%(B1,[hex(s(c)) for c in B1]))
print('  黑2    %r -> %s'%(B2,[hex(s(c)) for c in B2]))
open(r'F:\sr2-cn\_rec1_newnorm.txt','w',encoding='utf-8').write(newtxt)
open(r'F:\sr2-cn\_rec1_newgreen.txt','w',encoding='utf-8').write(GREENNEW)
print()
print('已写出 _rec1_newnorm.txt / _rec1_newgreen.txt')