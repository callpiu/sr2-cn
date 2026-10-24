# -*- coding: utf-8 -*-
"""在 SR2_pc.exe 里找字幕相关的字符串与函数线索。

目标
    交接文档说字幕由原生 C++ subtitles.cpp 绘制，与 vint 渲染器不同。
    找出这个路径用的字体名/函数名，反推它到底取哪个字体。
"""
import os, struct, re

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
d = open(os.path.join(G, "SR2_pc.exe"), "rb").read()
print("SR2_pc.exe %d 字节" % len(d))

KEYS = [b"subtitle", b"Subtitle", b"SUBTITLE", b"hud_msg", b"HUD_REGION_SUBTITLE",
        b"thin_overlay", b"subtitle_text", b"SubtitleText", b"draw_subtitle",
        b"nobdr", b"_nobdr.tga", b"fnt_body", b"font_info", b"font_alias"]

for k in KEYS:
    hits = []
    i = 0
    while True:
        j = d.find(k, i)
        if j < 0:
            break
        hits.append(j)
        i = j + 1
        if len(hits) > 12:
            break
    if hits:
        print("  %-22s %d 处: %s" % (k.decode("latin1"), len(hits), ["0x%X" % h for h in hits[:8]]))
    else:
        print("  %-22s 未找到" % k.decode("latin1"))
print()

# 打印所有出现在 .rdata 里的可打印字符串，含 font/subtitle 的更细看
RD_VA, RD_RAW, RD_SZ = 0x9B8000, 0x9B8000, 0xC8000
seg = d[RD_RAW:RD_RAW + RD_SZ]
strs = re.findall(rb"[\x20-\x7E]{5,80}", seg)
print("=== .rdata 里含 'font'/'subtitle'/'nobdr' 的字符串 ===")
n = 0
for s in strs:
    t = s.decode("latin1")
    low = t.lower()
    if ("font" in low) or ("subtitle" in low) or ("nobdr" in low):
        off = RD_RAW + seg.find(s)
        print("  0x%06X  %s" % (off, t))
        n += 1
        if n > 60:
            break
print("  (共 %d 条)" % n)
