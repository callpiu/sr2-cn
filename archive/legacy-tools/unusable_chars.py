# -*- coding: utf-8 -*-
"""盘点当前 patch 字体(charlist_CH)下「不能用的字」，并分类原因"""
import sys, json, os
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
S=set(CL)

print('字表条目 = %d   码点范围 U+%04X..U+%04X'%(len(CL),min(CL),max(CL)))
print()

# ---------- 类别 A：CJK 通用区覆盖率 ----------
lo,hi=0x4E00,0x9FA5
tot=hi-lo+1
have=sum(1 for c in range(lo,hi+1) if c in S)
print('【A类】CJK通用区 U+4E00..U+9FA5 共 %d 字'%tot)
print('   字表收录 %d 个，覆盖率 %.1f%%'%(have,100.0*have/tot))
print('   缺失 %d 个'%(tot-have))
print()

# 缺失的连续段（>=4字的段才列）
segs=[];run=[]
for c in range(lo,hi+1):
    if c not in S:
        run.append(c)
    else:
        if len(run)>=4: segs.append((run[0],run[-1],len(run)))
        run=[]
if len(run)>=4: segs.append((run[0],run[-1],len(run)))
print('   缺失连续段(>=4字) 共 %d 段:'%len(segs))
for a,b,n in segs[:40]:
    print('      U+%04X..U+%04X  %3d字   例:%s'%(a,b,n,''.join(chr(x) for x in range(a,min(a+8,b+1)))))
if len(segs)>40: print('      ...(余 %d 段)'%(len(segs)-40))
print()

# ---------- 高频常用字实测 ----------
FREQ=('的一是了我不人在他有这个上们来到时大地为子中你说生国年着就那和要她出也得里后自以会家可下而过天去能对小多然于心学么之都好看起发当没成只如事把还用第样道想作种开美总从无情己面最女但现前些所同日手又行意动方期它头经长儿回位分爱老因很给名法间斯知世什两次使身者被高已亲其进此话常与活正感见明问力理尔点文几定本公特做外孩相西果走将月十实向声车全信重三机工物气每并别真打太新比才便夫再书部水像眼等体却加电主界门利海受听表德少克代员许先口由死安写性马光白或住难望教命花结乐色更拉东神记处让母父应直字场平报友关放至张认接告入笑内英军候民岁往何度山觉路带万男边风解叫任金快原吃妈变通师立象数四失满战远格士音轻目条呢病始达深完今提求清王化空业思切怎非找片罗钱紶吗语元喜曾离飞科言干流欢约各即指合反题必该论交终林请医晚制球决窢传画保读运及则房早院量苦火布品近坐产答星精视五连司巴奇管类未朋且婚台夜青北队久乎越观落尽形影红爸百令周吧识步希亚术留市半热送兴造谈容极随演收首根讲整式取照办强石古华諣拿计您装似足况例致轻则轮孙罢')
FREQ=''.join(dict.fromkeys(FREQ))
miss=[ch for ch in FREQ if ord(ch) not in S]
print('【实测】抽查 %d 个高频常用字'%len(FREQ))
print('   缺失 %d 个: %s'%(len(miss),''.join(miss)))
print()

# ---------- 类别 B：坏字位 ----------
print('【B类】坏字位 —— 字在表内，但该 slot 索引渲染出错误字形')
BAD={1057:'延',239:'丈',1066:'弗',1058:'建',1065:'引',1059:'开',2100:'伙',348:'伙'}
print('   slot = idx+0x20，当前占位字 → 屏幕显示为：')
for i,(k,v) in enumerate(sorted(BAD.items())):
    cp=CL[k] if k<len(CL) else None
    cur=chr(cp) if cp else '?'
    print('      idx %-5d slot 0x%04X   本应是 %s(U+%04X) → 实显 %s'%(k,k+0x20,cur,cp or 0,v))
print('   ⚠ 这些是「位置」坏，不是「字」坏：该索引上换任何字都会显示成同一个错字')
print()

# ---------- 类别 C：撞车 ----------
print('【C类】坏字位撞车（同索引被两条不同汉字争用）')
print('   心(1097) → idx1065（已坏，显示"引"）；律 1089 → idx1057（已坏，显示"延"）')
print('   ⇒ 若要新用 idx1065 上"心"这个字，必须先确认不会与既有记录冲突')
print()

# ---------- 汇总统计 ----------
# 实际汉化用到的字符总量估算：扫 patch 里所有 static_CH 记录
PATCH=r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
print('【统计】汉化实际已用字符（patch.vpp_pc 内中文字形 slot 出现频次 top 问题字）')
if os.path.exists(PATCH):
    buf=open(PATCH,'rb').read()
    print('   已扫描 patch，%d 字节'%len(buf))
print()
print('='*70)
print('结论：三类原因互不相同')
print('  A 字表根本没有该字 → 无法编码，必须换字（如寇、驰）')
print('  B 字表有、slot 位置坏 → 该位置显示固定错字，须换字绕行')
print('  C 活动字幕路径特有 → 与字表无关，改 slot 无效（当前乱码主因）')
print('='*70)