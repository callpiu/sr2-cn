import sys, struct, os
sys.stdout.reconfigure(encoding='utf-8')

def load_cl(p):
    xs=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or l.startswith('//') or l.startswith('#'): continue
        xs.append(int(l))
    return xs

CL=load_cl(r'F:\sr2-cn\_juice_fix\charlist_CH.txt')
CL2={cp:i for i,cp in enumerate(CL)}
print('charlist_CH 条数 =',len(CL))

OLD='你的弟兄们需要你的保护'
NEW='一众伙伴临寇急待我驰援'
print()
print('原句 %r  字数=%d'%(OLD,len(OLD)))
print('新句 %r  字数=%d'%(NEW,len(NEW)))
print('长度差 = %+d'%(len(NEW)-len(OLD)))
print()

# 已确认的渲染坏字位（slot 索引 = charlist 索引）
BAD={1057:'延(律)',239:'丈(三)',1066:'弗(必)',1058:'建(徒)',1065:'引(心)',
     1059:'开(得)',2100:'伙(联)',348:'伙(会)'}

print('=== 新句每个字的 slot / charlist 索引 / 坏字位检查 ===')
ok=True
slots_new=[]
for ch in NEW:
    cp=ord(ch)
    idx=CL2.get(cp)
    if idx is None:
        print('  %s U+%04X  ✗ 字表里没有！'%(ch,cp)); ok=False; continue
    slot=idx+0x20
    slots_new.append(slot)
    flag='  <<< 已知坏字位 %s'%BAD[idx] if idx in BAD else ''
    print('  %s U+%04X -> idx=%-5d slot=0x%04X%s'%(ch,cp,idx,slot,flag))
print()
print('新句 slot 序列 =',[hex(s) for s in slots_new])
print()

print('=== 原句 slot 序列 ===')
slots_old=[]
for ch in OLD:
    cp=ord(ch); idx=CL2.get(cp)
    if idx is None:
        print('  %s U+%04X  ✗ 字表里没有'%(ch,cp)); continue
    slot=idx+0x20; slots_old.append(slot)
    flag='  <<< 已知坏字位 %s'%BAD[idx] if idx in BAD else ''
    print('  %s U+%04X -> idx=%-5d slot=0x%04X%s'%(ch,cp,idx,slot,flag))
print('原句 slot 序列 =',[hex(s) for s in slots_old])
print()

# 坏字位统计：新句用到多少已知坏字位
hits=[(ch,CL2[ord(ch)],BAD[CL2[ord(ch)]]) for ch in NEW if CL2.get(ord(ch)) in BAD]
print('新句命中已知坏字位：',hits if hits else '无')
hits_old=[(ch,CL2[ord(ch)],BAD[CL2[ord(ch)]]) for ch in OLD if CL2.get(ord(ch)) in BAD]
print('原句命中已知坏字位：',hits_old if hits_old else '无')

# 候选：11 字版本（保持等长）
print()
print('=== 若必须等长(11字)，补字候选 ===')
for pad in [' ','　','，','。','！','、','·']:
    cand=NEW+pad
    miss=[c for c in cand if CL2.get(ord(c)) is None]
    bid=[(c,BAD[CL2[ord(c)]]) for c in cand if CL2.get(ord(c)) in BAD]
    print('  +%r(%U+%04X) %r  字表缺失=%s  坏字位=%s'%(pad,ord(pad),cand,miss or '无',bid or '无'))