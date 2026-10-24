# -*- coding: utf-8 -*-
# 只读: 全量 lua 中所有 font 相关赋值
import os, sys, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))

PAT = re.compile(rb'(font|default_font|set_font|font_name)\s*[",)]', re.I)
tot = 0
for e in v.entries():
    if e['ext'].lower() != 'lua': continue
    d = v.read(e)
    if b'font' not in d.lower(): continue
    lines = d.decode("latin1").split("\n")
    hits = [(i+1, ln.strip()) for i, ln in enumerate(lines) if 'font' in ln.lower()]
    tot += len(hits)
    print("### %s.lua  (%d 处)" % (e['name'], len(hits)))
    for n, ln in hits:
        print("   %5d| %s" % (n, ln[:120]))
print("\n总 font 相关行数 =", tot)
