# -*- coding: utf-8 -*-
"""读 pause_map.lua，找区域名数据源"""
import sys, re, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
v=Vpp(r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc')
e=v.find('pause_map','lua')
d=bytes(v.read(e))
print('pause_map.lua size =',len(d))
s=d.decode('utf-8','replace')
# 找区域/地区相关
for kw in ('Downtown','Outskirts','district','District','region','Region','zone','neighborhood'):
    for m in re.finditer(kw,s):
        a=max(0,m.start()-120); b=min(len(s),m.end()+120)
        print('  [%s] ...%s...'%(kw,s[a:b].replace('\n',' | ')))
        break
print()
open(r'F:\sr2-cn\_pause_map.lua','w',encoding='utf-8').write(s)
print('已导出 -> F:/sr2-cn/_pause_map.lua')
# 所有 le_strings / xtbl 类条目
print()
print('=== 所有 le_strings / xtbl / txt 条目 ===')
for x in v.entries():
    if x['ext'] in ('le_strings','xtbl','txt','csv'):
        print('  %-32s %-12s size=%d'%(x['name'],x['ext'],x['size']))