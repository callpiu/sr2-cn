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
S=set(CL)
print('字表码点数 =',len(CL))
print('码点范围   = U+%04X .. U+%04X'%(min(CL),max(CL)))
# 分段覆盖
segs=[]; st=CL[0]; prev=CL[0]
for c in CL[1:]:
    if c!=prev+1:
        segs.append((st,prev)); st=c
    prev=c
segs.append((st,prev))
print('连续段数 =',len(segs))
big=[s for s in segs if s[1]-s[0]>200]
print('大于200字的连续段:')
for a,b in big: print('   U+%04X..U+%04X  (%d 字)'%(a,b,b-a+1))
print()

# 目标里两个缺字：寇 5BC7 驰 9A70 及其邻域是否整段缺
for tgt in ['寇','驰','盗','匪','敌','袭','侵','逼','危','急','待','援','驰','驱','赴','救','应','援','护','守','卫','抗','御','挡','阻','拦','援','帮','助','驰']:
    cp=ord(tgt)
    print('  %s U+%04X %s'%(tgt,cp,'✓在表 idx=%d'%CL.index(cp) if cp in S else '✗缺'), end='')
    # 邻域
    print('   邻域 U+%04X在表?%s'%(cp-1, cp-1 in S))
print()

print('=== 可用同义字盘点 ===')
cands='盗匪敌袭侵逼抵御挡拦救援应驰驱赴帮护守卫保庇护伙伴同袍兄弟众位'
for ch in cands:
    cp=ord(ch)
    print('  %s U+%04X %s'%(ch,cp,'✓ idx=%d slot=0x%04X'%(CL.index(cp),CL.index(cp)+0x20) if cp in S else '✗缺'))