import sys
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
BAD={1057:'延(律)',239:'丈(三)',1066:'弗(必)',1058:'建(徒)',1065:'引(心)',
     1059:'开(得)',2100:'伙(联)',348:'伙(会)'}

CANDS=[
 '一众伙伴临敌急待我救援',
 '一众伙伴临匪急待我救援',
 '一众伙伴遇敌急待我救援',
 '一众伙伴临敌急盼我救援',
 '一众伙伴临敌急待我驰援',
 '一众伙伴临敌急待我支援',
 '一众伙伴遭袭急待我救援',
 '一众伙伴临敌急待我驰援',
 '同袍伙伴临敌急待我救援',
 '一众兄弟临敌急待我救援',
]
OLD='你的弟兄们需要你的保护'
print('基准原句 %r (%d字)'%(OLD,len(OLD)))
print()
for c in CANDS:
    miss=[ch for ch in c if ord(ch) not in idx]
    bad=[(ch,BAD[idx[ord(ch)]]) for ch in c if ord(ch) in idx and idx[ord(ch)] in BAD]
    ok = (len(c)==len(OLD)) and not miss and not bad
    tag='✓ 可用' if ok else '✗'
    print('%s %r  %d字  缺字=%s  坏字位=%s'%(tag,c,len(c),miss or '无',bad or '无'))
    if ok:
        print('     slots=',[hex(idx[ord(ch)]+0x20) for ch in c])