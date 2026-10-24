# -*- coding: utf-8 -*-
# 只读穷举: 字体别名 -> 资源 的映射表到底在哪
import os, sys, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

KEYS = [b"thin_overlay", b"thin", b"header_n", b"bodyital_overlay",
        b"fnt_body_n", b"fnt_head_n", b"fnt_chinese", b"fnt_bodyital_n",
        b"ug-debug", b"font_hudsmall", b"jap"]

for tag, fn in [("patch", "patch.vpp_pc"), ("common", "common.vpp_pc")]:
    v = Vpp(os.path.join(G, fn))
    luas = [e for e in v.entries() if e['ext'].lower() in ('lua',)]
    print("=" * 70)
    print("[%s] lua 条目数 = %d" % (tag, len(luas)))
    for e in luas:
        d = v.read(e)
        hit = [k.decode() for k in KEYS if k in d]
        if hit:
            print("  %-42s %7dB  含: %s" % (e['name'] + '.' + e['ext'], len(d), ",".join(hit)))
