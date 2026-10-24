# -*- coding: utf-8 -*-
"""追踪 text_tag 的解析：字幕的文本与字体到底怎么绑定。

关键代码
    patch.vpp_pc / hud_msg.lua:
        o = vint_object_create("hud_msg", "text", region.anchor)
        vint_set_property(o, "text_tag", msg.text)
        vint_set_property(o, "font", "thin_overlay")

本脚本
    1. 找 vint 文档定义（common.vpp_pc 的 hud_msg.vint_doc）
       —— 里面可能有默认字体/字形设定
    2. 找 exe 里 "text_tag" / "thin_overlay" 的处理
    3. 找 vint_set_property 的实现（property 名字表）
"""
import os, sys, re

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUT = r"F:\sr2-cn\_fontfix_out"
os.makedirs(OUT, exist_ok=True)

# 1) hud_msg.vint_doc
print("=== common.vpp_pc / hud_msg.vint_doc ===")
with LightVpp(os.path.join(G, "common.vpp_pc")) as v:
    for e in v.entries():
        if v.name(e) == "hud_msg" and v.ext(e) == "vint_doc":
            d = v.read(e)
            p = os.path.join(OUT, "hud_msg.vint_doc")
            open(p, "wb").write(d)
            print("  %d 字节 -> %s" % (len(d), p))
            t = d.decode("utf-8", "replace")
            # 打印含 font 的部分
            for m in re.finditer(r'.{0,200}font.{0,300}', t, re.S):
                print("  ---")
                print("  %s" % m.group(0)[:500])
                break
            # 找所有 font 属性
            print()
            print("  含 'font' 的行:")
            for i, ln in enumerate(t.split("\n"), 1):
                if "font" in ln.lower():
                    print("    %4d: %s" % (i, ln.strip()[:160]))
print()

# 2) exe 里的关键字符串
print("=== exe 里 text_tag / vint 相关 ===")
d = open(os.path.join(G, "SR2_pc.exe"), "rb").read()
for k in (b"text_tag", b"text_scale", b"word_wrap", b"unscaled_size",
          b"vint_set_property", b"thin_overlay", b"font_info", b"font_alias",
          b"glyph", b"Glyph", b"charlist", b"cc_list"):
    hits = []
    i = 0
    while True:
        j = d.find(k, i)
        if j < 0:
            break
        hits.append(j)
        i = j + 1
        if len(hits) > 5:
            break
    print("  %-18s %s" % (k.decode("latin1"), ["0x%X" % h for h in hits] if hits else "未找到"))
