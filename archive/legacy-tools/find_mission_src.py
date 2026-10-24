# -*- coding: utf-8 -*-
"""用任务内部 ID (sh_rn_rec_center) 反查它在哪个字符串表里、
   以及该表用的槽位编码，从而找出任务显示名的真正来源。"""
import sys, os, re, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# 1) 从 VPP 里搜 ASCII 串 "sh_rn_rec_center" —— 找出承载它的资源
v = Vpp(os.path.join(G, "patch.vpp_pc"))
pat = b"sh_rn_rec_center"
print("### 在 patch.vpp_pc 各资源内搜 ASCII 'sh_rn_rec_center'")
for en in v.entries():
    try:
        d = bytes(v.read(v.find(en["name"], en["ext"])))
    except Exception:
        continue
    if pat in d:
        print("   %-28s %-12s %8d B  命中 %d 次"
              % (en["name"], en["ext"], len(d), d.count(pat)))

print("\n### VPP 原始字节层定位")
raw = open(os.path.join(G, "patch.vpp_pc"), "rb").read()
i = raw.find(pat)
while i >= 0:
    # 判断落在哪个 entry
    for en in sorted(v.entries(), key=lambda e: e["body"]):
        # 容器内偏移换算较复杂，这里只打印绝对位置
        pass
    print("   绝对偏移 0x%X" % i)
    break

# 2) 收集所有资源，检查哪些含 le_strings 结构且能解码出中文
print("\n### 列出 patch.vpp_pc 内所有含大量 ASCII 资源名的资源")
cands = []
for en in v.entries():
    ln = en["name"].lower()
    if any(k in ln for k in ("mission", "hood", "gang", "name", "title",
                             "activity", "stronghold", "job", "gangster")):
        d = bytes(v.read(v.find(en["name"], en["ext"])))
        cands.append((en["name"], en["ext"], len(d), d[:80]))
        print("   %-28s %-12s %8d B  %r" % (en["name"], en["ext"], len(d), d[:60]))
if not cands:
    print("   (无)")