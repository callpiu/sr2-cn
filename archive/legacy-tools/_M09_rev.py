# -*- coding: utf-8 -*-
# 反查直升机突击引用的字符串：搜 84F2.87ED（用户确证的那条乱码字幕）
# 找到引用它的活动文件，就能列出该活动的完整字符串集
import sys, os, struct
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

IDS = [(0x84F2, 0x87ED), (0x8858, 0x6942)]
needles = {}
for id1, id2 in IDS:
    needles["%04X.%04X" % (id1, id2)] = bytes([id1 & 0xFF, id1 >> 8, id2 & 0xFF, id2 >> 8])

print("搜索序列:")
for k, v in needles.items():
    print("  %s -> %s" % (k, v.hex(" ")))

hits = []
n = 0
for root, dirs, files in os.walk(G):
    if any(x in root.lower() for x in ("_backup", "pdb", ".venv", "sr2-cn")):
        continue
    for fn in files:
        p = os.path.join(root, fn)
        try:
            if os.path.getsize(p) > 40_000_000:
                continue
            with open(p, "rb") as f:
                data = f.read()
        except Exception:
            continue
        n += 1
        for tag, nd in needles.items():
            if nd in data:
                hits.append((tag, p, data.count(nd)))

print("\n扫描 %d 个文件，命中 %d 处" % (n, len(hits)))
for tag, p, c in hits[:40]:
    print("  %s  <- %s   x%d" % (tag, p.replace(G + os.sep, ""), c))
