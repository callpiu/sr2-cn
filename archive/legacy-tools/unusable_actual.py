# -*- coding: utf-8 -*-
"""实际汉化文本中用不了的字：扫 static_CH 全部记录"""
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
S=set(CL); idx={cp:i for i,cp in enumerate(CL)}

P=r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
buf=open(P,'rb').read()

# 解析 static_CH：头 <IHHI> -> buckets, count
import re
# 定位 static_CH 体：直接用已知记录起点附近反推不可靠，改用全表扫描
# 用法：所有 [id1][id2][slots...][0000] 结构太泛。
# 简化：扫全文所有 BE u16，取值落在 CJK 通用区或全角区的，当候选汉字
from collections import Counter
cnt=Counter()
buf2=buf
step=2
for i in range(0,len(buf2)-1,2):
    v=struct.unpack_from('>H',buf2,i)[0]
    if (0x4E00<=v<=0x9FA5) or (0x3000<=v<=0x303F) or (0xFF00<=v<=0xFFEF):
        cnt[v]+=1

print('扫描完成。文中出现的候选汉字(含误命中)种类 =',len(cnt))
print()
missing=[(cp,n) for cp,n in cnt.items() if cp not in S]
missing.sort(key=lambda x:-x[1])
print('=== 在字表中找不到的字（按出现次数降序）===')
if not missing:
    print('  无')
else:
    print('  种类 =',len(missing))
    for cp,n in missing[:60]:
        print('   %s U+%04X  出现 %d 次'%(chr(cp),cp,n))
    if len(missing)>60:
        print('   ...(余 %d 种)'%(len(missing)-60))
print()

# B类坏字位
BAD={239,348,1057,1058,1059,1065,1066,2100}
print('=== B类：已确认坏字位（该 slot 上换任何字都显示同一个错字）===')
for k in sorted(BAD):
    cp=CL[k]; cur=chr(cp)
    users=[chr(c) for c in cnt if idx.get(c)==k]
    print('  slot 0x%04X  当前字表第%d项=%s  误显为 %s'%(k+0x20,k,cur,{239:'丈',348:'伙',1057:'延',1058:'建',1059:'开',1065:'引',1066:'弗',2100:'伙'}[k]))
print()
print('  ⇒ 翻译时须避开这些 slot。已验证安全的高频替代字：')
safe='人帮计赚主城郊老如后新同界空'
print('   ',''.join(c for c in safe if c in S))
print()
print('=== A类高频常用字缺失（人工抽查）===')
for ch in '寇驰盼 deception'.replace(' ',''):
    print('   %s U+%04X  %s'%(ch,ord(ch),'✓在表' if ord(ch) in S else '✗缺字'))
print()
print('=== 已知人工确认缺字（11日/13日两次实测）===')
for ch in ['寇','驰','盼']:
    print('   %s U+%04X  %s'%(ch,ord(ch),'✓' if ord(ch) in S else '✗ 字表无此字，无法编码'))