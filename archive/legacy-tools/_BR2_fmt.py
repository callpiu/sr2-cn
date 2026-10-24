# -*- coding: utf-8 -*-
import os, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp

SRC = r"F:\sr2-cn\_patchsrc\patch.vpp_pc"          # 作者原版
GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"  # 当前游戏内

def dump(tag, b):
    print("-" * 80)
    print("[%s] size=%d md5=%s" % (tag, len(b), hashlib.md5(b).hexdigest()[:10]))
    crlf = b.count(b'\r\n'); lf = b.count(b'\n'); cr = b.count(b'\r')
    print("  \\r\\n=%d  \\n(total)=%d  \\r(total)=%d" % (crlf, lf, cr))
    print("  head 96 bytes:")
    print("   ", b[:96])
    print("  tail 96 bytes:")
    print("   ", b[-96:])
    print("  first 8 lines:")
    for i, ln in enumerate(b.split(b'\n')[:8]):
        print("    %2d: %r" % (i, ln[:80]))
    print("  last 6 lines:")
    for ln in b.split(b'\n')[-6:]:
        print("    %r" % (ln[:80],))

va = Vpp(SRC)
vg = Vpp(GAME)
for nm in ['charlist_CH', 'charlist_JP', 'charlist_SK', 'charlist_CZ']:
    e = va.find(nm)
    if e:
        dump("作者原版 " + nm, va.read(e))
    e = vg.find(nm)
    if e:
        dump("游戏内  " + nm, vg.read(e))
