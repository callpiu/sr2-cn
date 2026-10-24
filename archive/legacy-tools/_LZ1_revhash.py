# -*- coding: utf-8 -*-
# 反查：哪个任务/活动文件引用了字符串 id 8858.6942
# id 在文件中的字节序 = 两两 swap: 8858.6942 -> 58 88 42 69
import sys, os, struct, glob
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

needle = bytes([0x58, 0x88, 0x42, 0x69])   # 8858.6942 swap
needle2 = struct.pack("<I", 0x69428858)
print("搜索字节序列:", needle.hex(" "))

hits = []
n = 0
for root, dirs, files in os.walk(G):
    # 跳过备份/无关目录
    if any(x in root.lower() for x in ("_backup", "pdb", ".venv", "sr2-cn")):
        continue
    for fn in files:
        p = os.path.join(root, fn)
        try:
            if os.path.getsize(p) > 30_000_000:
                continue
            with open(p, "rb") as f:
                data = f.read()
        except Exception:
            continue
        n += 1
        if needle in data or needle2 in data:
            hits.append((p, len(data), data.count(needle) + data.count(needle2)))

print("扫描文件数 =", n)
print("\n=== 命中文件 ===")
for p, sz, c in hits[:40]:
    print("  %-90s %8d B  命中%d次" % (p.replace(G + os.sep, ""), sz, c))
