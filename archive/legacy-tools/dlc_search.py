# -*- coding: utf-8 -*-
"""用 DLC 专用格式（A84C7F73）解析 dlc_ch.le_strings，
   搜索「三王」「丈王」「辩护」——这是之前被静默跳过的盲区。"""
import sys, os, struct
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
P = os.path.join(G, "DLC", "Text", "dlc_ch.le_strings")
d = open(P, "rb").read()

# CH 字表
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in
       v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
slot2ch = {i + 0x20: chr(c) for i, c in enumerate(cps)}
print("CH 字表 %d 项" % len(cps))

magic = struct.unpack_from(">I", d, 0)[0]
N = struct.unpack_from(">I", d, 0x08)[0]
print("magic=%08X  N=%d  size=%d" % (magic, N, len(d)))
assert magic == 0xA84C7F73, "magic 不符"

# 桶表 0x0C 起128×(count,addr)；指针区 0x40C 起 N×u32；记录区 0x1364 起
PTR = 0x40C
ptrs = [struct.unpack_from(">I", d, PTR + i * 4)[0] for i in range(N)]
print("指针区首/末: 0x%X / 0x%X" % (ptrs[0], ptrs[-1]))
REC_BASE = 0x40C + N * 4
print("推算记录区起点 = 0x%X" % REC_BASE)


def dec(slots):
    return "".join(slot2ch.get(s, chr(s) if s < 0x20 else "?") for s in slots)


recs = []
for i, p in enumerate(ptrs):
    o = REC_BASE + p
    if o >= len(d):
        recs.append((i, p, None, None)); continue
    h = struct.unpack_from(">I", d, o)[0]
    slots, j = [], o + 4
    while j + 2 <= len(d):
        a, b2 = d[j], d[j + 1]
        if a == 0 and b2 == 0:
            break
        slots.append((a << 8) | b2)
        j += 2
    recs.append((i, p, h, slots))

ok = sum(1 for _, _, _, s in recs if s is not None)
print("成功解析 %d / %d 条" % (ok, N))

print("\n### DLC 全部文本（前 40 条抽样）")
for i, p, h, s in recs[:40]:
    if s:
        print("   [%3d] %r" % (i, dec(s)[:70]))

print("\n### 搜索目标词")
for w in ("三王", "丈王", "辩护", "律师"):
    hits = [(i, dec(s)) for i, p, h, s in recs if s and w in dec(s)]
    print("  [%s] %d 条" % (w, len(hits)))
    for i, t in hits[:10]:
        print("     [%3d] %r" % (i, t[:70]))

print("\n### 含「王」的 DLC 条目")
for i, p, h, s in recs:
    if s and "王" in dec(s):
        print("   [%3d] %r  slots=%s" % (i, dec(s)[:60], s[:12]))

print("\n### 含slot271(三) 的 DLC 条目")
for i, p, h, s in recs:
    if s and 271 in s:
        print("   [%3d] %r" % (i, dec(s)[:60]))