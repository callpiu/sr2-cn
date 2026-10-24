# -*- coding: utf-8 -*-
# 在 exe / DFEngine.dll 里找字符串引用名（SR2 的 text_tag 可能同时有名字形式）
# 目标：定位 "Your homies need your protection" 的引用方
import sys, os, re
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

CANDIDATES = [b"homies", b"protection", b"homies_need", b"HOMIES",
              b"protect_homies", b"PROTECT_HOMIES"]
files = []
for root, dirs, fs in os.walk(G):
    if any(x in root.lower() for x in ("_backup", "pdb", ".venv", "sr2-cn")):
        continue
    for fn in fs:
        if fn.lower().endswith((".exe", ".dll", ".dfo", ".cmo", ".luac")):
            p = os.path.join(root, fn)
            try:
                if os.path.getsize(p) < 60_000_000:
                    files.append(p)
            except Exception:
                pass
print("待扫文件:", [os.path.basename(p) for p in files])

for p in files:
    with open(p, "rb") as f:
        data = f.read()
    print("\n=== %s (%d B) ===" % (os.path.basename(p), len(data)))
    for pat in CANDIDATES:
        hits = [m.start() for m in re.finditer(re.escape(pat), data, re.I)]
        if hits:
            print("  %-16s x%d" % (pat.decode(), len(hits)))
            for h in hits[:6]:
                s = data[max(0, h - 40):h + 60]
                txt = "".join(chr(b) if 32 <= b < 127 else "." for b in s)
                print("      @0x%X  %s" % (h, txt))
