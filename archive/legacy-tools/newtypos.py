import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import CharList, file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
CL = CharList(CPS)
print("第三方字表 %d 项" % len(CPS))
print()
# 目标字
for ch in "辩护延师文王丈律孩":
    cp = ord(ch)
    if cp in CPS:
        i = CPS.index(cp)
        print("  %s U+%04X 索引 %-5d slot %-5d" % (ch, cp, i, i+0x20))
    else:
        print("  %s U+%04X 不在字表" % (ch, cp))
print()
# 在 patch 的文本表里搜「辩护」「延师」
d = bytes(v.read(v.find("static_CH","le_strings")))
b,c,oa,offs = file_offsets(d)
S = set(CPS)
targets = ["指定辩护延师", "前往", "文王", "老斯蒂尔沃特", "郊区", "任务"]
found = {}
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d)-10): continue
    u,_ = read_units(d, off+8)
    if u is None: continue
    vals = [x for x,_ in u]
    try:
        t = "".join(chr(CPS[x-0x20]) if 0x20 <= x-0x20 < len(CPS) else "?" for x in vals)
    except Exception:
        continue
    for tg in targets:
        if tg in t:
            found.setdefault(tg, []).append((off, t[:50], vals[:14]))
for tg in targets:
    print("=== %s ===" % tg)
    for off, t, vals in found.get(tg, [])[:4]:
        print("  @%-8d %s" % (off, t))
        print("            槽位: %s" % vals)
    if tg not in found: print("  （未找到）")
    print()
