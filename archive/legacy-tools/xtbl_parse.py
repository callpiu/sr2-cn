# -*- coding: utf-8 -*-
"""彻底解析 sr2_city_missions.xtbl —— 任务名真实来源。"""
import sys, os, re
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
p = os.path.join(G, "Mods", "sr2_city_missions.xtbl")
d = open(p, "rb").read()
print("文件 %s  %d 字节" % (p, len(d)))
print("前 16 字节 hex: %s" % d[:16].hex())
first = next((i for i, b in enumerate(d) if 32 <= b < 127), -1)
print("首个可打印字节位置=%d  预览=%r" % (first, d[:180]))

txt = None
for enc in ("utf-8", "utf-16-le", "utf-16", "gbk", "latin-1"):
    try:
        t = d.decode(enc)
        if t.count("<") > 10:
            txt = (enc, t); break
    except Exception:
        continue

if txt is None:
    print("\n无法按文本解码 -> 二进制表")
    sys.exit(0)

enc, t = txt
print("\n编码=%s 长度=%d  '<' x%d  含中文=%s"
      % (enc, len(t), t.count("<"),
         any('一' <= c <= '鿿' for c in t)))

print("\n### 搜索目标词")
for w in ("三王", "丈王", "辩护", "律师", "王"):
    n = t.count(w)
    print("  [%s] %d 次" % (w, n))
    for m in list(re.finditer(re.escape(w), t))[:3]:
        s = max(0, m.start() - 180)
        seg = t[s:m.end() + 180].replace("\r", " ").replace("\n", " ")
        print("      ...%s..." % seg[:340])

print("\n### 结构：所有标签名统计")
tags = re.findall(r"<([A-Za-z_][\w\.\-]*)", t)
from collections import Counter
for k, v in Counter(tags).most_common(25):
    print("   <%-28s x%d" % (k, v))

print("\n### 前 1500 字符")
print(t[:1500])