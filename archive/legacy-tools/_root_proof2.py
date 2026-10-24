# -*- coding: utf-8 -*-
"""用严格升序 rank 重建引擎行为"""
import sys, json, struct
sys.path.insert(0,'.')
from sr2lib import Vpp

def read_charlist_from_vpp(vpp_path, want='charlist_ch.txt'):
    v = Vpp(vpp_path)
    best=None
    for ent in v.entries():
        try:
            nm = ent.name
        except Exception:
            try: nm = ent[0]
            except Exception: nm=None
        if nm and str(nm).lower()==want:
            data=v.read(ent)
            txt=data.decode('utf-8','ignore')
            out=[]
            for line in txt.replace('\r','\n').split('\n'):
                line=line.split('//')[0].strip()
                if not line: continue
                try: out.append(int(line))
                except: pass
            return out, vpp_path
    return None, None

# 找有 charlist 的 vpp
import glob, os
found=None
for p in ['_v534_build.vpp_pc','_tmp_v532.vpp_pc']+sorted(glob.glob('_fix_candidates/patch_*.vpp_pc'))+sorted(glob.glob('pristine/*.vpp_pc')):
    if not os.path.exists(p): continue
    try:
        cl,src=read_charlist_from_vpp(p)
        if cl:
            print(f'{p}: n={len(cl)} head={cl[:6]} tail={cl[-4:]}')
            if found is None and len(cl)==2795:
                found=(cl,p)
    except Exception as e:
        print(p,'ERR',repr(e)[:80])
if found:
    PATCH_CL,PSRC=found
    print('\n选定 patch charlist:',PSRC,len(PATCH_CL))
else:
    print('\n!! 未找到 2795 charlist')

C2838=json.load(open('_day_2026-10-07/04_规则与数据/_expected_charlist.json',encoding='utf-8'))

PAIRS=[('们',332,'位'),('你',371,'任'),('保',391,'伪'),('兄',422,'巧'),
       ('弟',1035,'偶'),('护',1190,'该'),('的',1836,'璨'),('要',2296,'衡'),('需',2667,'雄')]

# 严格升序表：取 C2838 里满足升序的子序列? 或直接排序去重
SORTED=sorted(set(C2838))
print('SORTED(去重升序) n=',len(SORTED))

print('\n=== 假设A2: out = sorted_table[patch_cl_index] ===')
ok=0
for src,i,out in PAIRS:
    got=SORTED[i] if i<len(SORTED) else None
    ch=chr(got) if got else '?'
    h=(ch==out); ok+=h
    print(f'  {src} i={i:5d} -> {ch}')
print(f'  命中 {ok}/9')

print('\n=== 假设D: out 在 patch_cl 的索引 与 输入索引 的关系 ===')
for src,i,out in PAIRS:
    cp=ord(out)
    pi = PATCH_CL.index(cp) if cp in PATCH_CL else None
    print(f'  src={src}(i={i}) 显示={out}(cp={hex(cp)}) patch_cl位置={pi} (i-pi={i-pi if pi is not None else "-"})')
