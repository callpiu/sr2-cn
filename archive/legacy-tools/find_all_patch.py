# -*- coding: utf-8 -*-
"""全盘搜索所有 patch.vpp_pc 副本（确认游戏读的是哪一份）。"""
import os

SKIP = ("Windows", "Program Files", "$Recycle", "System Volume",
        "AppData\\Local\\Temp", "node_modules", ".git", "_fontfix_backup",
        "Steam\\steamapps\\downloading", "Steam\\steamapps\\shadercache")

found = []
for r in ("C:\\", "D:\\", "E:\\", "F:\\", "G:\\"):
    if not os.path.exists(r):
        continue
    for root, dirs, fs in os.walk(r):
        if any(s in root for s in SKIP):
            dirs[:] = []
            continue
        for f in fs:
            if f.lower() in ("patch.vpp_pc", "static_ch.le_strings", "charlist_ch.txt"):
                p = os.path.join(root, f)
                try:
                    sz = os.path.getsize(p)
                except Exception:
                    sz = -1
                found.append((p, sz))
                print("  %-88s %d" % (p, sz))
print()
print("共 %d 个" % len(found))
