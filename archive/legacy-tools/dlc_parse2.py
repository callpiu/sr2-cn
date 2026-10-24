# -*- coding: utf-8 -*-
"""DLC le_strings 正确解析：指针为文件内绝对偏移。"""
import sys, os, struct
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
d = open(os.path.join(G, "DLC", "Text", "dlc_ch.le_strings"), "rb").read()
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in
       v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
slot2ch = {i + 0x20: chr(c) for i, c in enumerate(cps)}
N = struct.unpack_from("<I", d, 0x08)[0]
PTR = 0x40C
ptrs = [struct.unpack_from("<I", d, PTR + i * 4)[0] for i in range(N)]
print("N=%d  指针 min=0x%X max=0x%X (EOF=0x%X)"
      % (N, min(ptrs), max(ptrs), len(d)))


def dec(slots):
    return "".join(slot2ch.get(s, chr(s) if s < 0x20 else "?") for s in slots)


def parse_at(o, be_hash):
    slots, j = [], o
    while j + 2 <= len(d):
        a, b2 = d[j], d[j + 1]
        if a == 0 and b2 == 0:
            return slots, j + 2
        slots.append((a << 8) | b2)
        j += 2
    return slots, j


recs = []
for i, p in enumerate(ptrs):
    s, end = parse_at(p, True)
    recs.append((i, p, s, end))
ok = sum(1 for _, _, s, _ in recs if s)
print("解析出 %d / %d 条非空" % (ok, N))

print("\n### 前 30 条")
for i, p, s, e in recs[:30]:
    if s:
        print("  [%3d] @0x%-6X %r" % (i, p, dec(s)[:66]))

print("\n############ 目标搜索 ############")
for w in ("三王", "丈王", "辩护", "律师"):
    hits = [(i, dec(s)) for i, p, s, e in recs if s and w in dec(s)]
    print("  [%s] %d 条" % (w, len(hits)))
    for i, t in hits[:12]:
        print("      [%3d] %r" % (i, t[:70]))

print("\n### 含「王」的 DLC 条目")
for i, p, s, e in recs:
    if s and "王" in dec(s):
        print("   [%3d] %rslots=%s" % (i, dec(s)[:56], s[:12]))

print("\n### 含 slot271(三) 的条目")
for i, p, s, e in recs:
    if s and 271 in s:
        print("   [%3d] %r" % (i, dec(s)[:64]))