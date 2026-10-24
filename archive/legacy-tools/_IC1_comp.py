# -*- coding: utf-8 -*-
# 穷举"组合映射"假设
import os, sys, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
OF = r"F:/sr2-cn/pristine/patch.vpp_pc"
def cl(buf):
    m=re.search(rb'count\s*=\s*(\d+)',buf); seg=buf[m.end():] if m else buf
    return [int(x) for x in re.findall(rb'\d+',seg)]
vG=Vpp(os.path.join(G,'patch.vpp_pc')); vO=Vpp(OF)
LC=cl(vG.read(vG.find('charlist_CH','txt')))
LO=cl(vO.read(vO.find('charlist_CH','txt')))
JP=cl(vG.read(vG.find('charlist_JP','txt')))
JP2=cl(vG.read(vG.find('JPCharList','txt')))
SK=cl(vG.read(vG.find('charlist_SK','txt')))
LISTS={'LC(汉化CH)':LC,'LO(官方CH)':LO,'JP':JP,'JPCharList':JP2,'SK':SK}

def idx(L, cp):
    try: return L.index(cp)
    except ValueError: return None

PAIRS=[(371,'任'),(1836,'璨'),(1035,'偶'),(422,'巧'),(332,'位'),
       (2667,'雄'),(2296,'衡'),(391,'伪'),(1190,'该')]

print("=== 组合映射: j = X.index( Y[i] ) ===")
for an, A in LISTS.items():
    for bn, B in LISTS.items():
        hit=0; miss=[]
        for i, disp in PAIRS:
            if i >= len(A): miss.append((i,'A范围外')); continue
            cp = A[i]
            k = idx(B, cp)
            if k is not None and k < len(LC) and chr(LC[k])==disp: hit+=1
            else: miss.append((i, k))
        if hit >= 3:
            print("  %s.index( %s[i] )  hit=%d/9  miss=%s" % (bn,an,hit,miss[:4]))

print("\n=== 组合映射(带偏移): j = B.index(A[i]) + d ===")
for an, A in LISTS.items():
    for bn, B in LISTS.items():
        for d in range(-6,7):
            hit=0
            for i, disp in PAIRS:
                if i>=len(A): continue
                k = idx(B, A[i])
                if k is None: continue
                kk = k+d
                if 0<=kk<len(LC) and chr(LC[kk])==disp: hit+=1
            if hit>=4:
                print("  %s.index(%s[i])+%d  hit=%d/9" % (bn,an,d,hit))

print("\n=== 直接: j = i + d ? ===")
for i,disp in PAIRS:
    print("   i=%4d j=%-5s 需要 d=%s" % (i, LC.index(ord(disp)) if ord(disp) in LC else '?', (LC.index(ord(disp))-i) if ord(disp) in LC else None))

print("\n=== j = A[i] 直接取值(即 显示字 == A[i]) ===")
for an,A in LISTS.items():
    hit=sum(1 for i,disp in PAIRS if i<len(A) and chr(A[i])==disp)
    print("   %-12s hit=%d/9" % (an,hit))
