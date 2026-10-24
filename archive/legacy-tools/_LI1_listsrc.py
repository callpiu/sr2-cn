# -*- coding: utf-8 -*-
# 步骤1：列出官方原版 / 汉化版 patch.vpp_pc 里的文本类资源（用纯 Python 的 sr2font.Vpp）
import sys, os
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
CN      = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"

for tag, p in (("官方原版", VANILLA), ("汉化版(当前)", CN)):
    if not os.path.exists(p):
        print("%s: 不存在 %s" % (tag, p)); continue
    v = Vpp(p)
    print("\n=== %s ===" % tag)
    for e in v.entries():
        n, x = (e["name"] or ""), (e["ext"] or "")
        if x in ("le_strings", "txt", "cxt", "") or "charlist" in n.lower():
            print("  %-34s %-11s %9d" % (n, x or "-", e["size"]))
