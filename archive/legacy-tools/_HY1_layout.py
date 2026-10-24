# -*- coding: utf-8 -*-
# 暴力求官方图集布局: P(k) = (x0+31*((k-A)%cols), y0+31*((k-A)//cols))
import os, sys, re, random
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
for i,c in enumerate(LC): posLC.setdefault(c, i)

# 汉化图集里每个字的模板
def tmpl_cn(ch):
    i = posLC.get(ord(ch))
    if i is None: return None
    x = 1+31*(i%65); y = 1+31*(i//65)
    return AG[y:y+31, x:x+31]

def ncc(a,b):
    a=a-a.mean(); b=b-b.mean()
    d=np.sqrt((a*a).sum())*np.sqrt((b*b).sum())
    return float((a*b).sum()/d) if d>1e-6 else 0.0

# 采样 k (>=94, 且该字在汉化表里)
random.seed(1)
cand = [k for k in range(100, len(LO)) if LO[k] in posLC]
sample = random.sample(cand, 60)
print("样本数", len(sample))

best=[]
for A in range(80, 130):
    for cols in (64,65,66,67):
        for x0 in (0,1,2):
            for y0 in (0,1,2,31,32,33,34):
                hit=0
                for k in sample:
                    m = k-A
                    if m < 0: continue
                    x = x0+31*(m%cols); y = y0+31*(m//cols)
                    if x+31>2048 or y+31>2048: continue
                    t = tmpl_cn(chr(LO[k]))
                    if t is None: continue
                    if ncc(t, AO[y:y+31, x:x+31]) > 0.90: hit+=1
                if hit >= 20:
                    best.append((hit, A, cols, x0, y0))
best.sort(reverse=True)
print("候选布局 (hit>=20):")
for b in best[:15]:
    print("   hit=%d  A=%d cols=%d x0=%d y0=%d" % b)
if not best:
    print("  无命中，放宽阈值再看最佳:")
    best=[]
    for A in range(80, 130):
        for cols in (64,65,66,67):
            for x0 in (0,1,2):
                for y0 in (0,1,2,31,32,33,34):
                    hit=0
                    for k in sample:
                        m=k-A
                        if m<0: continue
                        x=x0+31*(m%cols); y=y0+31*(m//cols)
                        if x+31>2048 or y+31>2048: continue
                        t=tmpl_cn(chr(LO[k]))
                        if t is None: continue
                        if ncc(t, AO[y:y+31,x:x+31])>0.90: hit+=1
                    best.append((hit,A,cols,x0,y0))
    best.sort(reverse=True)
    for b in best[:10]: print("   hit=%d A=%d cols=%d x0=%d y0=%d" % b)
