# -*- coding: utf-8 -*-
import os, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp
GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()[:12]

for p in [r"F:\sr2-cn\_patchsrc\patch.vpp_pc", r"F:\sr2-cn\_src2\patch.vpp_pc",
          r"F:\sr2-cn\_src2\patch.vpp_pc.原版对照",
          os.path.join(GAME, 'patch.vpp_pc'), os.path.join(GAME, 'common.vpp_pc')]:
    if os.path.exists(p):
        print(md5(p), os.path.getsize(p), p)

print("\n=== 各 VPP 中含 fnt / font / charlist / ui_ 的条目 ===")
for f in ['patch.vpp_pc', 'common.vpp_pc', 'textures.vpp_pc']:
    p = os.path.join(GAME, f)
    print("---", f)
    try:
        v = Vpp(p)
    except Exception as ex:
        print("   fail", ex); continue
    for e in v.entries():
        nm = e['name'].lower()
        if 'fnt' in nm or 'font' in nm or 'charlist' in nm:
            print("   %-34s %-10s size=%d" % (e['name'], e['ext'], e['size']))
