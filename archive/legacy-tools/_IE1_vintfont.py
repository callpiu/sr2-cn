# -*- coding: utf-8 -*-
# 扫描所有 vint_doc，统计各字体别名的出现位置
import os, sys, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

ALIASES = [b"thin_overlay", b"header_n_overlay", b"bodyital_overlay",
           b"thin", b"header_n", b"debug", b"font_hudsmall",
           b"fnt_chinese", b"fnt_body_n", b"fnt_head_n", b"jap"]

for tag, path in (("common", os.path.join(G,"common.vpp_pc")),
                  ("patch",  os.path.join(G,"patch.vpp_pc"))):
    v = Vpp(path)
    docs = [e for e in v.entries() if e['ext'].lower()=='vint_doc']
    print("\n===== %s : %d 个 vint_doc =====" % (tag, len(docs)))
    for e in docs:
        d = v.read(e)
        found = {}
        for a in ALIASES:
            n = d.count(a)
            if n: found[a.decode()] = n
        if found:
            print("  %-34s %s" % (e['name'], found))
