# -*- coding: utf-8 -*-
"""精确定位乱码索引关系"""
import sys, json, os
sys.path.insert(0,'.')
from sr2lib import Vpp

def read_cl(vpp_path, name='charlist_CH', ext='txt'):
    v=Vpp(vpp_path)
    for e in v.entries():
        if e['name']==name and e['ext']==ext:
            data=v.read(e); txt=data.decode('utf-8','ignore'); out=[]
            for line in txt.replace('\r','\n').split('\n'):
                line=line.split('//')[0].strip()
                if not line: continue
                try: out.append(int(line))
                except: pass
            return out
    return None

PCL=read_cl('_v534_build.vpp_pc')           # patch 2795
OFF=read_cl('pristine/patch.vpp_pc')        # 官方 2838
C2838=json.load(open('_day_2026-10-07/04_规则与数据/_expected_charlist.json',encoding='utf-8'))
print('PCL',len(PCL),'OFF',len(OFF),'JSON',len(C2838))

PAIRS=[('们',332,'位'),('你',371,'任'),('保',391,'伪'),('兄',422,'巧'),
       ('弟',1035,'偶'),('护',1190,'该'),('的',1836,'璨'),('要',2296,'衡'),('需',2667,'雄')]

print('\n输入字idx(slot-32) | 输出字在PCL的idx | 差 | 输出字在OFF的idx | 差')
for src,i,out in PAIRS:
    cp=ord(out)
    a=PCL.index(cp) if cp in PCL else None
    b=OFF.index(cp) if cp in OFF else None
    print(f'{src:>2} i={i:5d} | {out} PCL={a} (i-{a}={i-a if a is not None else "-"}) | OFF={b} (={i-b if b is not None else "-"})')

print('\n--- 检查: 输出字 = PCL[i] 的"下一个/前一个" ? ---')
for src,i,out in PAIRS:
    for d in (-2,-1,0,1,2):
        j=i+d
        if 0<=j<len(PCL) and chr(PCL[j])==out:
            print(f'  {src}(i={i}) -> {out} 命中 PCL[i{d:+d}]')
            break
    else:
        print(f'  {src}(i={i}) -> {out} 不在 PCL[i±2]')

print('\n--- 检查: 输出字码点 = 输入字码点 的线性变换? ---')
for src,i,out in PAIRS:
    a=ord(src); b=ord(out)
    print(f'  {src}({hex(a)}) -> {out}({hex(b)})  delta={b-a}')
