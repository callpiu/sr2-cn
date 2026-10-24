# -*- coding: utf-8 -*-
"""用真实 charlist_CH 计算：乱码字 与 正确字 的索引关系。"""
import sys
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v=Vpp(G+'/patch.vpp_pc')
txt=v.read(v.find('charlist_CH','txt')).decode()
ns=[int(t) for t in txt.split() if t.lstrip('-').isdigit()]
CL=ns
print("charlist_CH 项数 =", len(CL))
cp2i={cp:i for i,cp in enumerate(CL)}
def idx(ch):
    return cp2i.get(ord(ch))
pairs=[('任','你'),('璨','的'),('偶','弟'),('巧','兄'),('位','们'),
       ('雄','需'),('衡','要'),('伪','保'),('该','护')]
print("\n%-4s %-6s %-6s | %-8s %-8s %-8s | %s" % ("乱码","idx","cp","正确","idx","cp","d_idx  d_cp"))
for bad,good in pairs:
    ib=idx(bad); ig=idx(good)
    print("%-4s %-6s %-6s | %-8s %-8s %-8s | %s  %s" % (
        bad, ib, hex(ord(bad)), good, ig, hex(ord(good)),
        (ib-ig) if (ib is not None and ig is not None) else '?',
        (ord(bad)-ord(good)) if 1 else ''))
print()
# 关键: bad_idx vs good_idx 是否恒定差?
diffs=[]
for bad,good in pairs:
    ib=idx(bad); ig=idx(good)
    if ib is not None and ig is not None:
        diffs.append(ib-ig)
print("索引差集合:", set(diffs))
# 反向: 乱码字是否 = CL[good_idx + k]?
print("\n=== 检查 bad = CL[good_idx + k] ===")
for k in range(-200, 201):
    ok=all(idx(bad)==idx(good)+k for bad,good in pairs if idx(bad) is not None and idx(good) is not None)
    if ok:
        print("  ★ 恒等: bad_idx = good_idx + (%d)" % k)
        break
else:
    print("  没有恒定偏移")
# slot 视角: 乱码字在表中的 slot vs 正确字 slot
print("\n=== slot 视角 (slot=idx+32) ===")
for bad,good in pairs:
    ib=idx(bad); ig=idx(good)
    print("  %s(slot=%s)  <-  %s(slot=%s)   slot差=%s" % (
        bad, (ib+32) if ib is not None else '?',
        good, (ig+32) if ig is not None else '?',
        (ib-ig) if (ib is not None and ig is not None) else '?'))
