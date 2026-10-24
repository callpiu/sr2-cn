# -*- coding: utf-8 -*-
"""扫描游戏目录所有 VPP 容器，找出所有 charlist_* / fnt_* 资源。"""
import sys, os, glob
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# 收集所有 vpp 类文件（含子目录，但跳过 Mods/mods 与 Juiced 垃圾）
cands = []
for root, dirs, files in os.walk(G):
    dirs[:] = [d for d in dirs
               if d.lower() not in ("mods", "crashdumps", "__pycache__")]
    for f in files:
        if f.lower().endswith((".vpp_pc", ".vpp", ".vp2")):
            cands.append(os.path.join(root, f))

print("找到 %d 个 VPP 容器\n" % len(cands))
for p in sorted(cands):
    rel = os.path.relpath(p, G)
    try:
        v = Vpp(p)
        ents = v.entries()
    except Exception as e:
        print("  [跳过] %s  (%s)" % (rel, e))
        continue
    hits = []
    for en in ents:
        n, e = en["name"], en["ext"]
        ln = n.lower()
        if "charlist" in ln or ln.startswith("fnt") or "le_strings" in ln:
            hits.append((n, e, en["size"]))
    print("  %-52s entries=%-5d %s" % (rel, len(ents),
          ("<< " + ", ".join("%s.%s(%d)" % h for h in hits[:6])) if hits else ""))