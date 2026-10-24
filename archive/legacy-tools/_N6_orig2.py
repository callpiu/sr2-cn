# -*- coding: utf-8 -*-
import sys, re
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
v=Vpp(r'F:/sr2-cn/vpp_backup/patch.vpp_pc.orig')
raw=v.read(v.find('charlist_CH','txt'))
print("总大小 =", len(raw))
print("=== 前 500 字节 ===")
print(repr(raw[:500]))
print()
m=re.search(rb'count\s*=\s*(\d+)', raw[:400])
print("count =", m.group(1).decode() if m else "无 count=")
# 去注释后的数字
lines=raw.decode('latin1').splitlines()
data=[]
for ln in lines:
    s=ln.strip()
    if not s or s.startswith('//'): continue
    for t in s.split():
        if t.lstrip('-').isdigit(): data.append(int(t))
print("去注释后数字项数 =", len(data))
print("前 10 =", data[:10])
print("末 5 =", data[-5:])
# 是否首项=计数?
if data and data[0]==len(data)-1:
    print("★ 首项 == len-1 (%d) → 首项是计数" % data[0])
