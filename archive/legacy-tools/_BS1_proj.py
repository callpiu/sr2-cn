# -*- coding: utf-8 -*-
import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _vpp import Vpp
GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(GAME, 'common.vpp_pc'))
e = v.find('sr2', 'vint_proj')
b = v.read(e)
open(r'F:\sr2-cn\_sr2.vint_proj', 'wb').write(b)
print("size", len(b))
txt = b.decode('utf-8', 'replace')
# 打印包含 font 的片段
for m in re.finditer(r'font', txt, re.I):
    s = max(0, m.start() - 300)
    print("-----")
    print(txt[s:m.start() + 500])
    print()
