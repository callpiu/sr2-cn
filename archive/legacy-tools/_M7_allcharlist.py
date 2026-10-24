# -*- coding: utf-8 -*-
"""列出所有 vpp 里的 charlist*，以及 Mods 目录下所有 charlist 文件。"""
import sys, os, glob
sys.path.insert(0,'F:/sr2-cn')
from sr2lib import Vpp
G=r'G:/SteamLibrary/steamapps/common/Saints Row 2'
for vp in ['patch.vpp_pc','common.vpp_pc','misc.vpp_pc']:
    p=os.path.join(G,vp)
    if not os.path.exists(p): 
        print(vp,"不存在"); continue
    try:
        v=Vpp(p)
        hits=[e for e in v.entries() if 'charlist' in (e['name']+e['ext']).lower()]
        print("=== %s: %d 个 charlist ===" % (vp, len(hits)))
        for e in hits:
            print("   %-30s size=%d" % (e['name']+'.'+e['ext'], e['size']))
    except Exception as ex:
        print(vp,"ERR",ex)
print()
print("=== 磁盘上的 charlist 文件 ===")
for pat in ['**/charlist*','**/*harlist*']:
    for f in glob.glob(os.path.join(G,'**',pat), recursive=True):
        print("  %s  (%d bytes)" % (f, os.path.getsize(f)))
