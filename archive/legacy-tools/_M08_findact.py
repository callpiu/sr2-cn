# -*- coding: utf-8 -*-
# 找直升机突击（Heli Assault）的活动定义，列出它实际引用的字符串 hash
import sys, os, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

# 1) 文件名含 heli 的
print("=== 文件名含 heli 的文件 ===")
for root, dirs, files in os.walk(G):
    if any(x in root.lower() for x in ("_backup", "pdb", ".venv", "sr2-cn")):
        continue
    for fn in files:
        if "heli" in fn.lower():
            print("  %s" % os.path.join(root, fn).replace(G + os.sep, ""))

# 2) 所有 vpp 里条目名含 heli 的
print("\n=== vpp 内条目名含 heli / activity 的 ===")
for vf in ("patch.vpp_pc", "common.vpp_pc", "pegs.vpp_pc", "textures.vpp_pc"):
    p = os.path.join(G, vf)
    if not os.path.exists(p):
        continue
    try:
        v = Vpp(p)
    except Exception:
        continue
    for e in v.entries():
        n = (e["name"] or "").lower()
        if "heli" in n or (e["ext"] or "").lower() in ("xtbl", "lt2", "tbl"):
            print("  %-14s %-28s %-10s %9d" % (vf, e["name"], e["ext"] or "-", e["size"]))
