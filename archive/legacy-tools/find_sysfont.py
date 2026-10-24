# -*- coding: utf-8 -*-
"""找字幕用的系统字体名（D3DXCreateFontA 的 facename 参数）。

如果字幕用 D3DXCreateFontA（系统 TrueType 字体），
那么它【根本不使用游戏的 charlist/fnt_chinese 图集】，
中文能否显示取决于【系统字体是否含 CJK】以及【字体名是否设置正确】。
"""
import os, struct, re

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
d = open(os.path.join(G, "SR2_pc.exe"), "rb").read()
print("SR2_pc.exe %d 字节" % len(d))

# 找 D3DXCreateFontA 的引用点（IAT 或字符串）
i = d.find(b"D3DXCreateFontA")
print("D3DXCreateFontA 字符串 @ 0x%X" % i)
for k in range(max(0, i - 48), min(len(d), i + 48), 16):
    seg = d[k:k + 16]
    print("  %08X  %s  |%s|" % (k, " ".join("%02X" % x for x in seg),
                               "".join(chr(x) if 32 <= x < 127 else "." for x in seg)))
print()

# 常见的系统字体名（D3DX 默认字体）
FONTS = [b"Arial", b"arial", b"Tahoma", b"Verdana", b"Times New Roman",
         b"Microsoft Sans Serif", b"MS Sans Serif", b"Comic Sans MS",
         b"SimSun", b"\xcb\xce\xcc\xe5", b"Segoe UI", b"Lucida Console",
         b"Courier New", b"System", b"Microsoft YaHei", b"Gulim", b"MS Gothic",
         b"\xef\xbc\xad\xef\xbc\xb3"]  # MS Gothic UTF-8
print("=== 查找系统字体名 ===")
for f in FONTS:
    hits = []
    j = 0
    while True:
        k = d.find(f, j)
        if k < 0:
            break
        hits.append(k)
        j = k + 1
        if len(hits) > 5:
            break
    if hits:
        # 判断是否在 .rdata 字符串区
        loc = []
        for h in hits:
            if 0x9B8000 <= h < 0xA80000:
                loc.append("rdata")
            elif 0x1000 <= h < 0x9B7000:
                loc.append("text")
            else:
                loc.append("other")
        print("  %-24s %d 处  %s" % (f.decode("latin1", "replace"), len(hits),
                                     ["0x%X(%s)" % (h, l) for h, l in zip(hits, loc)]))
print()

# 列出 .rdata 中所有短的、像字体名的字符串（含空格、长度 5-30、字母开头）
RD_RAW, RD_SZ = 0x9B8000, 0xC8000
seg = d[RD_RAW:RD_RAW + RD_SZ]
strs = re.findall(rb"[\x20-\x7E]{4,40}", seg)
print("=== .rdata 中所有可疑的「字体名」候选（含空格、非全大写、非路径）===")
n = 0
for s in strs:
    t = s.decode("latin1")
    if "\\" in t or "/" in t or "%" in t or "." in t and not t.endswith(".ttf"):
        continue
    if not t[0].isalpha():
        continue
    if t.isupper():
        continue
    # 允许 1-3 个单词
    words = t.split()
    if 1 <= len(words) <= 4 and all(w[0].isupper() or w.islower() for w in words):
        off = RD_RAW + seg.find(s)
        print("  0x%06X  %s" % (off, t))
        n += 1
        if n > 50:
            break
print("  (共 %d 条)" % n)
