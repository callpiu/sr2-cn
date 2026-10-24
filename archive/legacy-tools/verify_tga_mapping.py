# -*- coding: utf-8 -*-
"""验证：描述符里的 .tga 文件名是否对应 textures.vpp_pc 的条目名。

如果对应，那么改描述符的文件名 = 换图集，且【不用碰 textures.vpp_pc】。
"""
import os, re, sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# 1) pegs 里所有字体描述符的文件名
print("=== pegs.vpp_pc 字体描述符的 .tga 名 ===")
tga_names = {}
with LightVpp(os.path.join(G, "pegs.vpp_pc")) as pv:
    for e in pv.entries():
        nm = pv.name(e)
        if "fnt_" in nm or "vint" in nm:
            d = pv.read(e)
            i = d.find(b".tga")
            if i > 0:
                s = i
                while s > 0 and 32 <= d[s - 1] < 127:
                    s -= 1
                fn = d[s:i + 4].decode("latin1")
                tga_names[nm] = fn
                print("  %-26s -> %s" % (nm, fn))
print()

# 2) textures 里是否有对应条目（去掉 _nobdr.tga 后缀去找）
print("=== textures.vpp_pc 里是否有这些资源名 ===")
tex_names = set()
with LightVpp(os.path.join(G, "textures.vpp_pc")) as tv:
    for e in tv.entries():
        tex_names.add(tv.name(e) + ("." + tv.ext(e) if tv.ext(e) else ""))
        tex_names.add(tv.name(e))

for nm, fn in sorted(tga_names.items()):
    base = fn.replace("_nobdr.tga", "").replace(".tga", "")
    found = []
    for cand in (base, base + ".tga", fn, nm):
        if cand in tex_names:
            found.append(cand)
    print("  %-26s 文件名=%-28s 命中: %s" % (nm, fn, found if found else "无"))
print()

# 3) 列出 textures 里所有 fnt_* 条目（含扩展名）
print("=== textures.vpp_pc 全部 fnt_* 条目 ===")
with LightVpp(os.path.join(G, "textures.vpp_pc")) as tv:
    for e in tv.entries():
        nm = tv.name(e)
        if nm.startswith("fnt_") or "font" in nm.lower():
            print("  #%-6d %-30s %-10s %9d" % (e["idx"], nm, tv.ext(e) or "-", e["size"]))
print()

# 4) patch.vpp_pc 里是否有 fnt_chinese 的 .tga
print("=== patch.vpp_pc 全部 fnt_* 条目 ===")
with LightVpp(os.path.join(G, "patch.vpp_pc")) as pv:
    for e in pv.entries():
        nm = pv.name(e)
        if nm.startswith("fnt_"):
            print("  #%-6d %-30s %-10s %9d" % (e["idx"], nm, pv.ext(e) or "-", e["size"]))
