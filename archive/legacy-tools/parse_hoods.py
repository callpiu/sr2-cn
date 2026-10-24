# -*- coding: utf-8 -*-
"""完整解析 Hoods XML：列出所有 DISTRICT_/HOOD_ 标识符与所有字段"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G=r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v=Vpp(G+r'\patch.vpp_pc')
d=bytes(v.read(v.find('Hoods','')))
s=d.decode('latin-1')
open(r'F:\sr2-cn\_Hoods.xml','w',encoding='utf-8').write(s)
print('已导出 _Hoods.xml (%d 字节)'%len(s))
print()
print('=== 所有 <Name> 值 ===')
names=re.findall(r'<Name>([^<]*)</Name>',s)
for x in names: print('   %s'%x)
print('共',len(names))
print()
print('=== 所有出现的标签 ===')
tags=set(re.findall(r'<([A-Za-z_]+)>',s))
for t in sorted(tags): print('   %s'%t)
print()
print('=== 所有 DISTRICT_ / HOOD_ 标识符（去重）===')
ids=sorted(set(re.findall(r'\b(DISTRICT_[A-Z_]+|HOOD[A-Z_]*)\b',s)))
for x in ids: print('   %s'%x)
print('共',len(ids))