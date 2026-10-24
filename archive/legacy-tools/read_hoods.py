# -*- coding: utf-8 -*-
"""读 patch.vpp_pc 里的 Hoods 条目 —— 这应���是区域名表"""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G=r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v=Vpp(G+r'\patch.vpp_pc')
e=v.find('Hoods','')
print('entry:',e)
d=bytes(v.read(e))
print('size =',len(d))
print('前 256 字节 hex:')
for o in range(0,min(256,len(d)),16):
    seg=d[o:o+16]
    print('  %04X  %s  %s'%(o,seg.hex(' '),''.join(chr(x) if 32<=x<127 else '.' for x in seg)))
print()
print('=== 尝试 ASCII 解读 ===')
s=d.decode('latin-1')
print(repr(s[:400]))
print()
# 搜可打印片段
import re
segs=re.findall(r'[\x20-\x7e]{3,}',s)
print('可打印片段 =',len(segs))
for x in segs[:40]: print('   %r'%x)