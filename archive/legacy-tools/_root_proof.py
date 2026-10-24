# -*- coding: utf-8 -*-
"""决定性验证：引擎把 charlist(patch 2795) 索引当作 common 表(2838)索引使用"""
import sys, json, struct, glob
sys.path.insert(0, '.')
from sr2lib import Vpp

# ---- 1) 取 patch 里的 charlist_CH.txt (2795) ----
def get_charlist(vpp_path, name='charlist_CH.txt'):
    v = Vpp(vpp_path)
    for ent in v.entries():
        n = getattr(ent, 'name', None) or ent[0]
        if str(n).lower().endswith('charlist_ch.txt') or str(n).lower()=='charlist_ch.txt':
            data = v.read(ent)
            txt = data.decode('utf-8', 'ignore')
            out=[]
            for line in txt.replace('\r','\n').split('\n'):
                line=line.split('//')[0].strip()
                if not line: continue
                try: out.append(int(line))
                except: pass
            return out
    return None

for p in ['_v534_build.vpp_pc','_tmp_v532.vpp_pc']:
    try:
        cl=get_charlist(p)
        if cl:
            print(f'{p}: charlist_CH n={len(cl)} head={cl[:8]}')
            PATCH_CL=cl; PATCH_VPP=p
            break
    except Exception as e:
        print(p,'ERR',e)

# ---- 2) v37 期望表 (2838) ----
C2838=json.load(open('_day_2026-10-07/04_规则与数据/_expected_charlist.json',encoding='utf-8'))
print('C2838 n=',len(C2838))

# ---- 3) 9 条实测错位映射 ----
# (输入字, 输入字在 charlist 的索引, 引擎实际显示的字)
PAIRS=[('们',332,'位'),('你',371,'任'),('保',391,'伪'),('兄',422,'巧'),
       ('弟',1035,'偶'),('护',1190,'该'),('的',1836,'璨'),('要',2296,'衡'),('需',2667,'雄')]

print('\n=== 假设A: engine_out_code = C2838[ patch_cl_index ] ===')
ok=0
for src,i,out in PAIRS:
    got = C2838[i] if i < len(C2838) else None
    ch = chr(got) if got else '?'
    hit = (ch==out)
    ok+=hit
    print(f'  src={src} idx={i:5d} -> C2838[{i}]={ch}({hex(got) if got else "-"})  实测={out}  {"OK" if hit else "x"}')
print(f'  命中 {ok}/9')

print('\n=== 假设B: 输入按 slot 值(=idx+0x20)索引 C2838 ===')
ok=0
for src,i,out in PAIRS:
    s=i+0x20
    got = C2838[s] if s < len(C2838) else None
    ch = chr(got) if got else '?'
    hit=(ch==out); ok+=hit
    print(f'  src={src} slot={s:5d} -> C2838[{s}]={ch}  实测={out}  {"OK" if hit else "x"}')
print(f'  命中 {ok}/9')

print('\n=== 假设C: 输出字在 charlist 里的索引 -> C2838 反查 ===')
# 引擎可能: 用 patch_cl 索引 i 去 C2838 取值 -> 得字X; 再... 不, 直接看 X 在 patch_cl 的索引
for src,i,out in PAIRS:
    got = C2838[i]
    ch=chr(got)
    # 该输出字 out 的码点
    cp=ord(out)
    # out 在 patch_cl 里的位置
    try: pi=PATCH_CL.index(cp)
    except ValueError: pi=None
    print(f'  src={src}(cl_i={i}) -> C2838[{i}]={ch} ; 实测显示字 {out} 的码点 {hex(cp)} 在patch_cl位置={pi}')
