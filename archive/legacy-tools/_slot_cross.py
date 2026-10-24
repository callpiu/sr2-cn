# -*- coding: utf-8 -*-
"""★ 决定性验证：按 loadcharlist 真实规则算 slot, 跨表反查"""
import sys
sys.path.insert(0,'.')
from sr2lib import Vpp

def read_cl(p,n='charlist_CH',e='txt'):
    v=Vpp(p)
    for x in v.entries():
        if x['name']==n and x['ext']==e:
            cps=[]
            for l in v.read(x).decode('utf-8','ignore').replace('\r','\n').split('\n'):
                l=l.split('//')[0].strip()
                if l.isdigit(): cps.append(int(l))
            return cps
    return None

def build_table(cps):
    """按 0x7F4430 规则构造: (码点, slot) 列表"""
    tbl=[]; counter=0x100
    for cp in cps:
        if cp < 0x100:
            slot=cp
        else:
            slot=counter; counter+=1
        tbl.append((cp,slot))
    return tbl

PATCH=read_cl('_v534_build.vpp_pc')
OFF=read_cl('pristine/patch.vpp_pc')
print('patch',len(PATCH),'official',len(OFF))

TP=build_table(PATCH)     # 当前游戏载入的表
TO=build_table(OFF)       # 官方繁体表
# 反查: slot -> 码点
def slot2cp(tbl): return {s:c for c,s in tbl}
MP=slot2cp(TP); MO=slot2cp(TO)

PAIRS=[('们',0x4EEC,'位'),('你',0x4F60,'任'),('保',0x4FDD,'伪'),('兄',0x5144,'巧'),
       ('弟',0x5F1F,'偶'),('护',0x62A4,'该'),('的',0x7684,'璨'),('要',0x8981,'衡'),('需',0x9700,'雄')]

print('\n=== 假设X: 文本slot按【官方2838表】编, 游戏用【patch 2795表】反查 ===')
ok=0
for src,cp,out in PAIRS:
    if cp in {c for c,_ in TO}:
        slot=dict((c,s) for c,s in TO)[cp]     # 官方表里该字的 slot
        got=MP.get(slot)
        ch=chr(got) if got else '?'
        h=(ch==out); ok+=h
        print(f'  {src}({hex(cp)}) OFF-slot={slot} -> patch反查={ch}({hex(got) if got else "-"})  实测={out} {"OK" if h else "x"}')
    else:
        print(f'  {src}({hex(cp)}) 不在官方表')
print(f'  命中 {ok}/9')

print('\n=== 假设Y: 文本slot按【patch表】编, 游戏用【官方表】反查 ===')
ok=0
for src,cp,out in PAIRS:
    if cp in {c for c,_ in TP}:
        slot=dict((c,s) for c,s in TP)[cp]
        got=MO.get(slot)
        ch=chr(got) if got else '?'
        h=(ch==out); ok+=h
        print(f'  {src} patch-slot={slot} -> official反查={ch}  实测={out} {"OK" if h else "x"}')
    else:
        print(f'  {src} 不在patch表')
print(f'  命中 {ok}/9')

# 打印源字的两种slot, 及输出字所在位置
print('\n=== 参考: 源字/输出字在两张表的 slot ===')
SP=dict((c,s) for c,s in TP); SO=dict((c,s) for c,s in TO)
print('字 | patch_slot | official_slot')
for src,cp,out in PAIRS:
    print(f'{src} {hex(cp)} | {SP.get(cp)} | {SO.get(cp)}   ||| 输出{out} patch_slot={SP.get(ord(out))} official_slot={SO.get(ord(out))}')
