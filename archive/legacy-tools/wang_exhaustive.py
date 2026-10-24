# -*- coding: utf-8 -*-
"""彻底定位「丈王」：
   1) CH 表全量导出，找所有含「王」的**完整**条目（含被截断的）
   2) 关键：CH 表里凡「王」前面的字若为「三」-> 找「王」的所有前缀
   3) 直接在 CH 表槽位层面搜 [任何字, 1796] 且首字为 slot271(三)
"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
sys.stdout.reconfigure(encoding="utf-8")
from collections import Counter

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in
       v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
slot2ch = {i + 0x20: chr(c) for i, c in enumerate(cps)}


def dec(slots):
    return "".join(slot2ch.get(s, chr(s) if s < 0x20 else "?") for s in slots)


d = bytes(v.read(v.find("static_CH", "le_strings")))
b, c, off_at, offs = file_offsets(d)

recs = []
for off in offs:
    r = read_units(d, off + 8)
    if not r or not r[0]:
        continue
    slots = [x for x, _ in r[0]]
    recs.append((off, struct.unpack_from("<HH", d, off), slots, dec(slots)))

print("### static_CH 全量 %d 条" % len(recs))

print("\n### 所有含「王」的条目（完整）")
n = 0
for o, r, s, t in recs:
    if "王" in t:
        n += 1
        print("   @%-8d %r" % (o, t))
print("   共 %d 条" % n)

print("\n### 「王」作为第1/2 字的所有条目（找「三王」「丈王」型）")
for o, r, s, t in recs:
    if t.startswith("王") or (len(t) > 1 and t[1] == "王"):
        print("   @%-8d %rslots=%s" % (o, t[:30], s[:6]))

print("\n### 槽位层面：任何条目含 slot=1796(王) 且前一槽是 271(三)")
hit = 0
for o, r, s, t in recs:
    for i in range(1, len(s)):
        if s[i] == 1796 and s[i - 1] == 271:
            print("   ★ @%-8d %r  slots=%s" % (o, t, s))
            hit += 1
print("   命中 %d" % hit)

print("\n### 含 slot=271(三) 的所有条目")
for o, r, s, t in recs:
    if 271 in s:
        print("   @%-8d %r" % (o, t[:50]))

print("\n### 含 slot=270(丈) 的所有条目")
for o, r, s, t in recs:
    if 270 in s:
        print("   @%-8d %r" % (o, t[:50]))