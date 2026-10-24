# -*- coding: utf-8 -*-
"""全局搜索：所有 vpp_pc 里是否有 charlist_CH（含 common/textures/pegs 等）。"""
import sys, os, glob
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
for p in sorted(glob.glob(os.path.join(G, '*.vpp_pc'))):
    try:
        v = Vpp(p)
    except Exception as e:
        print("%-20s ERR %s" % (os.path.basename(p), e)); continue
    hits = [e for e in v.entries() if 'charlist' in (e['name'] + e['ext']).lower()]
    if hits:
        print("%s:" % os.path.basename(p))
        for e in hits:
            print("    %-28s size=%d" % (e['name'] + '.' + e['ext'], e['size']))
print()
print("=== DLC 目录 ===")
for p in sorted(glob.glob(os.path.join(G, 'DLC', '**', '*.vpp_pc'), recursive=True)):
    try:
        v = Vpp(p)
        hits = [e for e in v.entries() if 'charlist' in (e['name'] + e['ext']).lower()]
        if hits:
            print("%s:" % p)
            for e in hits:
                print("    %-28s size=%d" % (e['name'] + '.' + e['ext'], e['size']))
    except Exception:
        pass
print()
print("=== 磁盘上的 charlist 松散文件 ===")
found = False
for dp, dn, fn in os.walk(G):
    for f in fn:
        if 'charlist' in f.lower():
            print("   ", os.path.join(dp, f), os.path.getsize(os.path.join(dp, f))); found = True
if not found:
    print("   （无）")
