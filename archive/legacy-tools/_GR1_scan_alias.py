# -*- coding: utf-8 -*-
"""只读穷举扫描：在 common/patch/pegs/textures 里找出所有包含字体别名或字体资源名的文件。
目的：定位「别名 -> 字体文件」映射表真正存放的位置（proj? vint_doc? xtbl?）。"""
import sys, os, re
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
TARGETS = [b"thin_overlay", b"thin", b"fnt_body_n", b"fnt_body_s",
           b"fnt_chinese", b"header_n_overlay", b"bodyital_overlay"]
# 只关心能「定义」别名的：出现 thin_overlay 字面量
NEEDLES = [b"thin_overlay", b"fnt_body_n", b"fnt_chinese"]

FILES = ["common.vpp_pc", "patch.vpp_pc", "pegs.vpp_pc", "textures.vpp_pc"]

for fn in FILES:
    p = os.path.join(G, fn)
    if not os.path.exists(p):
        print("MISS", fn); continue
    print("=" * 70)
    print(f"### {fn}  ({os.path.getsize(p):,} B)")
    v = Vpp(p)
    ents = v.entries()
    print(f"entries = {len(ents)}")
    hits = 0
    for e in ents:
        try:
            body = v.read(e)
        except Exception as ex:
            continue
        found = [n.decode() for n in NEEDLES if n in body]
        if found:
            hits += 1
            nm = e['name'] + ('.' + e['ext'] if e['ext'] else '')
            print(f"  HIT {nm:42s} size={e['size']:>9} -> {found}")
    if hits == 0:
        print("  (无命中)")
print("=" * 70)
print("DONE")
