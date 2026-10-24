# -*- coding: utf-8 -*-
import sys
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
p=r'F:/sr2-cn/vpp_backup/patch.vpp_pc.orig'
import os
print("size =", os.path.getsize(p))
v=Vpp(p)
for e in v.entries():
    n=e['name']+'.'+e['ext']
    if 'charlist' in n.lower() or n.lower().endswith('.txt'):
        print("  %-30s size=%d" % (n, e['size']))
print()
raw=v.read(v.find('charlist_CH','txt'))
print("=== 官方 charlist_CH 前 300 字节 ===")
print(repr(raw[:300]))
print()
import re
m=re.search(rb'count=(\d+)', raw[:200])
print("count =", m.group(1).decode() if m else "无")
ns=[int(x) for x in raw.split()]
print("总 token 数 =", len(ns))
print()
# 当前补丁 charlist_CH 项数
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
v2=Vpp(G+'/patch.vpp_pc')
raw2=v2.read(v2.find('charlist_CH','txt'))
ns2=[int(x) for x in raw2.split()]
print("当前补丁 charlist_CH token 数 =", len(ns2))
print("前 5 =", ns2[:5])
