# -*- coding: utf-8 -*-
"""决定性根因验证 v3 —— 用正确 Vpp API"""
import sys, json, os, glob
sys.path.insert(0,'.')
from sr2lib import Vpp

def read_cl(vpp_path, name='charlist_CH', ext='txt'):
    v=Vpp(vpp_path)
    for e in v.entries():
        if e['name']==name and e['ext']==ext:
            data=v.read(e)
            txt=data.decode('utf-8','ignore')
            out=[]
            for line in txt.replace('\r','\n').split('\n'):
                line=line.split('//')[0].strip()
                if not line: continue
                try: out.append(int(line))
                except: pass
            return out
    return None

# --- 读 patch 版 charlist (2795) ---
PATCH_CL=None; PSRC=None
for p in ['_v534_build.vpp_pc','_tmp_v532.vpp_pc']+sorted(glob.glob('_fix_candidates/patch_*.vpp_pc')):
    if not os.path.exists(p): continue
    cl=read_cl(p)
    if cl:
        print(f'{p}: n={len(cl)}')
        if PATCH_CL is None or len(cl)==2795:
            PATCH_CL=cl; PSRC=p
            if len(cl)==2795: break
print('选中:',PSRC,len(PATCH_CL) if PATCH_CL else None)

# --- 官方 pristine ---
OFF_CL=None
for p in sorted(glob.glob('pristine/*.vpp_pc'))+['pristine/patch.vpp_pc']:
    if not os.path.exists(p): continue
    cl=read_cl(p)
    if cl:
        print(f'{p}: n={len(cl)}  (官方)')
        OFF_CL=cl; break

# --- v37 JSON ---
C2838=json.load(open('_day_2026-10-07/04_规则与数据/_expected_charlist.json',encoding='utf-8'))

PAIRS=[('们',332,'位'),('你',371,'任'),('保',391,'伪'),('兄',422,'巧'),
       ('弟',1035,'偶'),('护',1190,'该'),('的',1836,'璨'),('要',2296,'衡'),('需',2667,'雄')]

def test(name, tbl, off=0):
    if tbl is None: print(f'{name}: N/A'); return
    ok=0; res=[]
    for src,i,out in PAIRS:
        j=i+off
        ch=chr(tbl[j]) if 0<=j<len(tbl) else '?'
        h=(ch==out); ok+=h
        res.append(f'{src}->{ch}')
    print(f'{name} 命中{ok}/9 : '+' '.join(res))

print('\n--- 各种「用 patch_cl 索引 去查表」的组合 ---')
test('A: C2838[i]      ', C2838, 0)
test('B: C2838[i+0x20] ', C2838, 0x20)
test('C: C2838[i-0x20] ', C2838, -0x20)
if OFF_CL: test('D: OFF_CL[i]     ', OFF_CL, 0)
if OFF_CL: test('E: OFF_CL[i+0x20]', OFF_CL, 0x20)
test('F: PATCH_CL[i]   ', PATCH_CL, 0)

print('\n--- 9 条的表内排名法 ---')
print('输入字 | patch_cl索引 | 输出字 | 输出在C2838位置 | 输出在PATCH_CL位置')
for src,i,out in PAIRS:
    cp=ord(out)
    p1=C2838.index(cp) if cp in C2838 else None
    p2=PATCH_CL.index(cp) if (PATCH_CL and cp in PATCH_CL) else None
    print(f'  {src} | {i:5d} | {out} | C2838={p1} | PCL={p2}')
