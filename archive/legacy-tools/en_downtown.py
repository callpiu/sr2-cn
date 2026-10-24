# -*- coding: utf-8 -*-
"""从英文 static_US 里抽 Downtown / Outskirts 相关串，用于核对「城区」译法"""
import os, sys, struct, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
OFF = r"F:\sr2-cn\_ref_第三方补丁\原始基准\patch_第三方原版.vpp_pc"
v=Vpp(OFF)
e=v.find('static_US','le_strings')
d=bytes(v.read(e))
u=d.decode('utf-16-le','ignore')
# 抽取所有可打印 ASCII 片段
segs=re.findall(r'[\x20-\x7e]{3,}',u)
kw=('Downtown','Outskirts','downtown','outskirts')
seen=set()
print('=== 含 Downtown / Outskirts 的英文串 ===')
for s in segs:
    if any(k in s for k in kw):
        if s in seen: continue
        seen.add(s)
        print('  %s'%s[:150])
print()
print('总片段 =',len(segs),' 命中 =',len(seen))