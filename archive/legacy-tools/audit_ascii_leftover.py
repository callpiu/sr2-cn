# -*- coding: utf-8 -*-
"""盘点中文表里所有「折中译名」痕迹 = 中文表中残留的 ASCII 片段。
   方法：定位中文表区间 → 按 0000 分隔遍历记录边界 → 检查记录内是否含ASCII slot。
   ★ 绝不能"全盘扫码点字节"（会出几万种误命中），必须先定记录边界。"""
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

def is_ascii_slot(v): return 0x21<=v<=0x7E
def cjk_ratio(t):
    if not t: return 0
    return sum(1 for c in t if '\u4e00'<=c<='\u9fff')/len(t)

# 中文表区间：由已知中文记录界定
# @0x1C6AE60 / @0x2E0CC3A 是中文；@0x1D8A230 是德文 => 中文表分两段
SEGMENTS=[(0x1C00000,0x1C80000,'中文表A'),(0x2E00000,0x2E40000,'中文表B')]

results={}
for lo,hi,name in SEGMENTS:
    hits=[]
    p=lo
    while p<hi and p+2<=len(buf):
        v=struct.unpack_from('>H',buf,p)[0]
        if v!=0:
            # 收集一条记录
            q=p; slots=[]
            while q+2<=len(buf):
                w=struct.unpack_from('>H',buf,q)[0]
                if w==0: break
                slots.append(w); q+=2
            t=''.join(dec(w) for w in slots)
            has_ascii=any(is_ascii_slot(w) for w in slots)
            # 中文为主 且 含 ASCII => 折中痕迹
            if has_ascii and cjk_ratio(t)>=0.2:
                hits.append((p,slots,t))
            p=q+2
        else:
            p+=2
    results[name]=hits

total=0
for name,hits in results.items():
    print('='*76)
    print('【%s】中文为主但含 ASCII 的记录：%d 条'%(name,len(hits)))
    print('='*76)
    total+=len(hits)
    seen=set()
    for p,slots,t in hits:
        key=t
        if key in seen: continue
        seen.add(t)
        print('  @0x%08X %2d字 %r'%(p,len(slots),t))
print()
print('去重后种类 =', total)