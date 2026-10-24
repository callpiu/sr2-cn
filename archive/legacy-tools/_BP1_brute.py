# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.insert(0,'.')
from _vpp import Vpp
gv=Vpp(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc')
def pc(buf):
    out=[]
    for ln in buf.decode('latin-1').splitlines():
        s=ln.strip()
        if not s or s.startswith('//') or s.startswith('count'): continue
        try: out.append(int(s))
        except: pass
    return out
cl=pc(gv.read(gv.find('charlist_CH')))

# S1: 源字 -> slot -> 渲染出的字形索引
S1 = [('你',403,336),('的',1868,1784),('弟',1067,410),('兄',454,967),('们',364,362),
      ('需',2699,2656),('要',2328,2268),('保',423,354),('护',1222,2342)]
S2 = [('你',403,336),('的',1868,1784),('弟',1067,410),('兄',454,967),('们',364,362),
      ('要',2328,1458),('出',510,2268),('去',613,535),('谈',2389,2491),('几',502,2234),
      ('笔',1995,287),('生',1824,1292),('意',1159,354),('，',2822,2342),('保',423,301),
      ('护',1222,362),('他',356,2514),('们',364,417),('免',460,543),('遭',2563,458),
      ('袭',2312,1243),('击',511,1221)]

def test(name, data, keyfn, valfn):
    pts=[(keyfn(sl), v) for _,sl,v in data]
    ok=all(a==b for a,b in pts)
    # 检测是否单一映射
    d={}
    bad=0
    for k,v in pts:
        if k in d and d[k]!=v: bad+=1
        d[k]=v
    return bad

print('S1 单一映射冲突(按slot):', test('x',S1,lambda s:s,lambda s:s))
print('S2 单一映射冲突(按slot):', test('x',S2,lambda s:s,lambda s:s))

# 暴力: glyph = (a*key + b) mod M
def brute(data, keyfn, Mmax=6000):
    res=[]
    pts=[(keyfn(sl), v) for _,sl,v in data]
    for M in range(300, Mmax):
        (k1,v1),(k2,v2) = pts[0], pts[1]
        dk=(k2-k1)%M; dv=(v2-v1)%M
        # 解 a*dk = dv mod M
        import math
        g=math.gcd(dk,M)
        if dv % g: continue
        dk2, dv2, M2 = dk//g, dv//g, M//g
        try:
            inv=pow(dk2,-1,M2)
        except ValueError:
            continue
        a0=(dv2*inv)%M2
        for t in range(g):
            a=a0+t*M2
            b=(v1-a*k1)%M
            if all((a*k+b)%M==v for k,v in pts):
                res.append((M,a,b))
    return res

for label, data in [('S1',S1),('S2',S2)]:
    for kname, kf in [('slot',lambda s:s), ('slot-32',lambda s:s-32)]:
        r=brute(data, kf)
        print(f'{label} key={kname}: linear solutions={r[:6]}')

# 暴力: glyph = (key * a) >> shift
print()
for label,data in [('S1',S1),('S2',S2)]:
    found=[]
    pts=[(sl,v) for _,sl,v in data]
    for shift in range(1,16):
        for a in range(1,200000):
            if all(((sl*a)>>shift)==v for sl,v in pts):
                found.append((shift,a))
                break
    print(f'{label} (slot*a)>>shift:', found[:5])
