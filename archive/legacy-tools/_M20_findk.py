# -*- coding: utf-8 -*-
"""穷举：找 k 使 CL[(idx+k) mod N] == 乱码字。
同时试: 正确字的 slot 直接查表 / 用不同表 / 模运算 / 等等。
"""
import sys
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
CH=[int(t) for t in v.read(v.find('charlist_CH','txt')).decode().split() if t.lstrip('-').isdigit()]
N=len(CH); cp2i={cp:i for i,cp in enumerate(CH)}

correct="你的弟兄们需要你的保护"
screen ="任璨偶巧位雄衡任璨伪该"
print("len(correct)=%d len(screen)=%d" % (len(correct), len(screen)))
sid=[cp2i.get(ord(c)) for c in screen]
cid=[cp2i.get(ord(c)) for c in correct]
print("correct idx:", cid)
print("screen  idx:", sid)
print()

# 试各种线性关系 sid = a*cid + b (mod N)  — 用前两对解，再验证
print("=== 试 sid = (cid + k) mod N ===")
for k in range(-N, N):
    if all(sid[i]==(cid[i]+k)%N for i in range(len(cid)) if sid[i] is not None and cid[i] is not None):
        print("  命中 k=%d" % k)
print()
print("=== 试 sid = (slot + k) mod N, slot=cid+32 ===")
for k in range(-N,N):
    if all(sid[i]==((cid[i]+32)+k)%N for i in range(len(cid)) if sid[i] is not None and cid[i] is not None):
        print("  命中 k=%d" % k)
print()
print("=== 试 sid = CL[(cid+k)] 直接用中文码点 ===")
# 也许 screen char 是由 codepoint 经 charlist 查得
# 试 screen_char = chr(CH[(codepoint-32)])  等
for expr,k in [("cp-32",32),("cp",0)]:
    res=""
    for ch in correct:
        u=ord(ch)
        i=u-k
        res += chr(CH[i]) if 0<=i<N else '?'
    print("  %s -> %s" % (expr, res))
print()
# 关键: 用 JPCharList 等别的表, 以正确字 slot 索引
print("=== 用别的表 T[slot_CH(正确字)] ===")
for nm in ['charlist_JP','charlist_SK','JPCharList','charlist_CZ']:
    T=[int(t) for t in v.read(v.find(nm,'txt')).decode().split() if t.lstrip('-').isdigit()]
    res=""
    for ch in correct:
        i=cp2i.get(ord(ch))
        if i is None: res+='?'; continue
        slot=i+32
        res += chr(T[slot]) if 0<=slot<len(T) else '?'
    print("  %-14s -> %s" % (nm,res))
print()
# 用别的表 T[slot - 32]
print("=== 用别的表 T[idx_CH(正确字)] ===")
for nm in ['charlist_JP','charlist_SK','JPCharList','charlist_CZ']:
    T=[int(t) for t in v.read(v.find(nm,'txt')).decode().split() if t.lstrip('-').isdigit()]
    res=""
    for ch in correct:
        i=cp2i.get(ord(ch))
        if i is None: res+='?'; continue
        res += chr(T[i]) if 0<=i<len(T) else '?'
    print("  %-14s -> %s" % (nm,res))
