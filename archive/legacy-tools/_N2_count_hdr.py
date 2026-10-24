# -*- coding: utf-8 -*-
"""验证: 官方原版 charlist_CH 是否有 count= 头? 当前补丁的有吗?"""
import sys, glob, os
sys.path.insert(0,'F:/sr2-cn')
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'

print("=== 当前 patch.vpp_pc 里的 charlist_CH ===")
from sr2lib import Vpp
v=Vpp(G+'/patch.vpp_pc')
raw=v.read(v.find('charlist_CH','txt'))
print("  前 100 字节:", raw[:100])
print("  含 b'count=' :", b'count=' in raw[:300])
print()

print("=== 历史产物 ===")
for p in sorted(glob.glob('_archive/output*/charlist_CH')) + ['fontwork/charlist_final.bin','fontwork/charlist_new.bin']:
    if not os.path.exists(p): continue
    raw=open(p,'rb').read()
    first=raw.split(b'\n')[0][:60]
    print("  %-42s %6d B  首行=%r  含count=%s" % (p, len(raw), first, b'count=' in raw[:300]))
print()
# 找 expected_charlist.json
for p in glob.glob('*.json'):
    if 'charlist' in p.lower():
        print("  JSON:", p, os.path.getsize(p))
