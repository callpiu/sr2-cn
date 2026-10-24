# -*- coding: utf-8 -*-
import os, sys, re
import numpy as np
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
OF = r"F:/sr2-cn/pristine/patch.vpp_pc"

def cl(buf):
    m = re.search(rb'count\s*=\s*(\d+)', buf)
    seg = buf[m.end():] if m else buf
    return [int(x) for x in re.findall(rb'\d+', seg)]

vG = Vpp(os.path.join(G,"patch.vpp_pc")); vO = Vpp(OF)
LC = cl(vG.read(vG.find("charlist_CH","txt")))
LO = cl(vO.read(vO.find("charlist_CH","txt")))
_, aG = dxt3_decode(vG.read(vG.find("fnt_chinese",None)), 2048, 2048)
_, aO = dxt3_decode(vO.read(vO.find("fnt_chinese",None)), 2048, 2048)
AG = aG.astype(np.float32); AO = aO.astype(np.float32)
posLC = {}
for i,c in enumerate(LC): posLC.setdefault(c,i)

def ncc(a,b):
    a=a-a.mean(); b=b-b.mean()
    d=np.sqrt((a*a).sum())*np.sqrt((b*b).sum())
    return float((a*b).sum()/d) if d>1e-6 else 0.0

def tmpl_cn(cp):
    i = posLC.get(cp)
    if i is None: return None
    x=1+31*(i%65); y=1+31*(i//65)
    return AG[y:y+31, x:x+31]

# 对每个官方 charlist 序号 k，在官方图集上找其字形出现在哪
print("=== 逐个官方序号 k，在官方图集网格上找最佳匹配 ===")
print("   (检查 P(k)=(1+31*(k%%C),1+31*(k//C)) 对 C=65,66 的命中)")
for C in (65, 66):
    hit = 0; tested = 0
    for k in range(94, min(len(LO), 2795)):
        t = tmpl_cn(LO[k])
        if t is None: continue
        tested += 1
        x = 1+31*(k%C); y = 1+31*(k//C)
        if x+31 > 2048 or y+31 > 2048: continue
        if ncc(t, AO[y:y+31, x:x+31]) > 0.90: hit += 1
        if tested > 400: break
    print("   C=%d : hit=%d / tested=%d" % (C, hit, tested))

# 直接看: 官方图集里 你 在哪里 (全网格扫描 65 列)
t_ni = tmpl_cn(ord("你"))
print("\n=== 官方图集(65列网格)中与「你」最像的格子 ===")
res=[]
for row in range(43):
    for col in range(65):
        x=1+31*col; y=1+31*row
        if x+31>2048 or y+31>2048: continue
        res.append((ncc(t_ni, AO[y:y+31,x:x+31]), col, row))
res.sort(reverse=True)
for s,c,r in res[:6]:
    k = r*65+c
    print("   corr=%.3f cell=%4d(col%2d,row%2d)  该格官方应为LO[%d]=%s" % (s,k,c,r,k, chr(LO[k]) if k<len(LO) else '?'))

# 反过来: 官方图集 cell k 实际是什么字？——用汉化模板全表匹配
print("\n=== 官方图集 cell 336/371/391 实际字形 -> 在汉化表中反查 ===")
for k in (336, 371, 391, 1035, 1190, 1836, 2296, 2667, 332, 422, 967, 354, 410, 1784, 2268, 2656, 2342):
    x=1+31*(k%65); y=1+31*(k//65)
    cellimg = AO[y:y+31, x:x+31]
    best=(0,None)
    for i in range(0, min(len(LC), 2795), 1):
        t = AG[1+31*(i//65)*31 - 31*(i//65) + 31*(i//65):1+31*(i//65)+31, 1+31*(i%65):1+31*(i%65)+31] if False else None
    # 简化：只对少量候选算
    cands = [posLC[c] for c in [0x4F60,0x4EFB,0x7684,0x74A0,0x5F1F,0x5076,0x5144,0x5DE7,0x4EEC,0x4F4D,0x9700,0x96C4,0x8981,0x8861,0x4FDD,0x4F2A,0x62A4,0x8BE5] if c in posLC]
    for i in cands:
        t = AG[1+31*(i//65):1+31*(i//65)+31, 1+31*(i%65):1+31*(i%65)+31]
        v = ncc(t, cellimg)
        if v > best[0]: best = (v, chr(LC[i]))
    print("   官方cell %4d 最像 = %s (corr=%.3f)" % (k, best[1], best[0]))
