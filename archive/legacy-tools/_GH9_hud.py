# -*- coding: utf-8 -*-
"""GH9: 1) 搜所有 VPP 里 name 含 hud 的条目; 2) 搜游戏目录松散 vint_proj; 3) 松散 lua 清单。"""
import sys, os, glob, re
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

print("=== 1) VPP 里 name 含 hud 的条目 ===")
for vp in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    try:
        v = Vpp(vp)
    except Exception:
        continue
    hits = []
    for e in v.entries():
        nm = (e["name"] or "")
        if re.search(r"hud", nm, re.I):
            hits.append("%s.%s (%d B)" % (nm, e["ext"], e["size"]))
    if hits:
        print("[%s]" % os.path.basename(vp))
        for h in sorted(set(hits)):
            print("   ", h)

print("\n=== 2) 松散 vint_proj / 相关文件 ===")
for pat in ("**/*.vint_proj", "**/hud*.lua", "**/*.lua"):
    fs = glob.glob(os.path.join(G, pat), recursive=True)
    if fs:
        print("[%s] %d 个" % (pat, len(fs)))
        for f in fs[:40]:
            print("   ", os.path.relpath(f, G), os.path.getsize(f))

print("\n=== 3) Mods 目录下所有 lua ===")
md = os.path.join(G, "Mods")
if os.path.isdir(md):
    for f in sorted(os.listdir(md)):
        if f.lower().endswith(".lua"):
            print("   ", f, os.path.getsize(os.path.join(md, f)))
