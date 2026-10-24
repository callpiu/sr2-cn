# -*- coding: utf-8 -*-
"""决定性假说：文本 slot 正确，但渲染时用了【别的语言 charlist】查字形。
验证：用 CH 的 slot 值, 去索引其它语言表的 idx，看能否得到正确字。
反过来也验证: 正确字的 CH-slot = 乱码字在【某表】的 idx ?
"""
import sys
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
tabs={}
for nm in ['charlist_CH','charlist_CZ','charlist_JP','charlist_PL','charlist_RU','charlist_SK','JPCharList']:
    try:
        txt=v.read(v.find(nm,'txt')).decode()
        ns=[int(t) for t in txt.split() if t.lstrip('-').isdigit()]
        if ns and ns[0]==len(ns)-1: ns=ns[1:]
        tabs[nm]=ns
        print("%-14s %d 项, 前3=%s" % (nm, len(ns), [hex(x) for x in ns[:3]]))
    except Exception as e:
        print(nm,"ERR",e)
print()
CH=tabs['charlist_CH']
cp2i={cp:i for i,cp in enumerate(CH)}

pairs=[('任','你'),('璨','的'),('偶','弟'),('巧','兄'),('位','们'),
       ('雄','需'),('衡','要'),('伪','保'),('该','护')]

# 假说A: 乱码字 = T[CH_slot(正确字)]  (T=某表, 索引直接用slot)
print("=== 假说A: 乱码字 == T[ slot_CH(正确字) ] ===")
for nm,T in tabs.items():
    hits=0
    for bad,good in pairs:
        sg=cp2i.get(ord(good))
        if sg is None: continue
        slot=sg+32
        if 0<=slot<len(T) and T[slot]==ord(bad):
            hits+=1
    if hits: print("  %-14s 命中 %d/%d" % (nm, hits, len(pairs)))

# 假说B: 乱码字索引 = 正确字在别的表里的位置
print("\n=== 假说B: idx_CH(乱码字) == idx_T(正确字) for some T ===")
for nm,T in tabs.items():
    p2={cp:i for i,cp in enumerate(T)}
    hits=0
    for bad,good in pairs:
        ib=cp2i.get(ord(bad)); ig=p2.get(ord(good))
        if ib is not None and ig is not None and ib==ig: hits+=1
    print("  %-14s 命中 %d/%d" % (nm, hits, len(pairs)))

# 假说C: 乱码字 = T[ idx_CH(正确字) ]  (索引直接用，不加32)
print("\n=== 假说C: 乱码字 == T[ idx_CH(正确字) ] ===")
for nm,T in tabs.items():
    hits=0
    for bad,good in pairs:
        sg=cp2i.get(ord(good))
        if sg is None: continue
        if 0<=sg<len(T) and T[sg]==ord(bad): hits+=1
    if hits: print("  %-14s 命中 %d/%d" % (nm, hits, len(pairs)))

# 假说D: 乱码字 = T[ idx_CH(正确字) - 32 ]
print("\n=== 假说D: 乱码字 == T[ slot_CH(正确字) - 32 ] == T[idx] ===")
print("(同C)")

# 展示: 正确字 slot_CH = ? 而 乱码字 在 CH 的 idx = ?
print("\n=== 数据表 ===")
print("%-4s %-4s | %-10s %-10s" % ("乱码","正确","bad_idx_CH","good_slot_CH"))
for bad,good in pairs:
    ib=cp2i.get(ord(bad)); sg=cp2i.get(ord(good))
    print("%-4s %-4s | %-10s %-10s" % (bad,good,ib,(sg+32) if sg is not None else '?'))
