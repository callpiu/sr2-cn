# -*- coding: utf-8 -*-
"""收窄：只找「折中译名」痕迹 = 连续 2+ 个 ASCII 字母，且不是已知正常词。
   排除：占位符 %ls %s %d %0、{XXX_IMG}、纯数字、常见专名、品牌。"""
import sys, struct, re
sys.stdout.reconfigure(encoding='utf-8')
P=r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
buf=open(P,'rb').read()
CL=[]
for l in open(r'F:\sr2-cn\_juice_fix\charlist_CH.txt',encoding='utf-8'):
    l=l.strip()
    if not l or l.startswith('//') or l.startswith('#'): continue
    CL.append(int(l))
def dec(s): return chr(CL[s-0x20]) if 0x20<=s<0x20+len(CL) else '<%04X>'%s

WHITELIST={
 'Xbox','Pimpcane','Friendly','Fire','David','Banner','Cocks','Bag','Boy','Go',
 'Ultor','Maero','Kazuo','Tera','Gryphon','Masako','Johnny','Gat','Carlos','Mendoza',
 'Dex','Hektor','Hughes','Bradshaw','Troy','Valderama','Jane','Mr','Mrs',
 'Kanto','Feed','Dogs','Poseidon','Philips','Phillips','Building','Elysian','Fields',
 'Shivington','Saints','Row','Stilwater','Loastaub','Sansetti','Roach','Mike','Mikey',
 'Marlboro','Rounds','Square','Mr','Sunshine','Reaper','Carnales','Gowanus','Tigra','Mr','Bigg',
 'Viking','CEO','RAGE','HD','TV','FBI','NBA','UFC','SF','X','Dungeon',
}
def is_ascii_slot(v): return 0x21<=v<=0x7E
def cjk_ratio(t):
    return sum(1 for c in t if '\u4e00'<=c<='\u9fff')/len(t) if t else 0

SEGMENTS=[(0x1C00000,0x1C80000,'表A'),(0x2E00000,0x2E40000,'表B')]
out=[]
for lo,hi,name in SEGMENTS:
    p=lo
    while p<hi and p+2<=len(buf):
        v=struct.unpack_from('>H',buf,p)[0]
        if v!=0:
            q=p; slots=[]
            while q+2<=len(buf):
                w=struct.unpack_from('>H',buf,q)[0]
                if w==0: break
                slots.append(w); q+=2
            t=''.join(dec(w) for w in slots)
            # 提取连续 ASCII 字母块(>=2)
            for m in re.finditer(r'[A-Za-z]{2,}',t):
                w=m.group(0)
                if w in WHITELIST: continue
                ctx=t[max(0,m.start()-6):m.end()+6]
                out.append((p,name,w,len(slots),ctx,t))
                break
            p=q+2
        else:
            p+=2

# 按 ASCII 词归类
from collections import defaultdict
g=defaultdict(list)
for p,name,w,L,ctx,t in out:
    g[w].append((p,name,ctx,L))
print('=== 中文表中的「非白名单」连续 ASCII 词%d 种 ==='%len(g))
print()
# 按长度排，最可疑在前（4+字母、且上下文有中文）
sus=[(w,v) for w,v in g.items() if len(w)>=3]
sus.sort(key=lambda x:-len(x[1]))
for w,v in sus[:45]:
    sample=v[0]
    print('  %-14s 出现 %2d 次  例 %r'%(w,len(v),sample[2]))
print()
print('=== 逐条列出 len>=4 的词（高可信折中痕迹）===')
for w,v in sus:
    if len(w)<4: continue
    print()
    print('--- %s (%d 条) ---'%(w,len(v)))
    for p,name,ctx,L in v[:6]:
        print('   @0x%08X [%s] %d字  ctx=%r'%(p,name,L,ctx))