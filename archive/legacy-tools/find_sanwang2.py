# -*- coding: utf-8 -*-
"""锁定「三王」：在 static_US 里穷举所有可能译为「三王」的英文名，
   再逐个查 CH 侧对应条目。
   候选：Three Kings / 3 Kings / Kings / The Three / Tri Kings ...
   注意 US 解码须skip=2。"""
import sys, os, struct, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in
       v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
slot2ch = {i + 0x20: chr(c) for i, c in enumerate(cps)}
LIM = 0x20 + len(cps)


def dec(slots):
    return "".join(slot2ch.get(s, chr(s) if s < 0x20 else "\uFFFD")
                   for s in slots)


def load(name, skip):
    d = bytes(v.read(v.find(name, "le_strings")))
    b, c, off_at, offs = file_offsets(d)
    out = []
    for off in offs:
        r = read_units(d, off + 8 + skip)
        if not r or not r[0]:
            continue
        slots = [x for x, _ in r[0]]
        out.append((off, struct.unpack_from("<HH", d, off), slots))
    return out


us = load("static_US", 2)
ch = load("static_CH", 0)
print("US %d 条 / CH %d 条" % (len(us), len(ch)))

# CH 里含「王」的条目
ch_wang = [(o, r, s, dec(s)) for o, r, s in ch if "王" in dec(s)]
print("\n### CH 含「王」的条目 %d 条" % len(ch_wang))
for o, r, s, t in ch_wang:
    print("   @%-8d resID=%s %r" % (o, r, t[:60]))

# US 里含 King 的**短**条目（任务名多为短名）
print("\n### US 含 'King' 的短条目(<=40字符)")
us_k = [(o, r, s, dec(s)) for o, r, s in us if "king" in dec(s).lower()
        and len(dec(s)) <= 40]
for o, r, s, t in us_k:
    print("   @%-8d resID=%s %r" % (o, r, t))

# 「三王」最可能 = "Three Kings"；穷举所有变体
print("\n### US 中所有含 'three' 的短条目")
for o, r, s in us:
    t = dec(s)
    if "three" in t.lower() and len(t) <= 40:
        print("   @%-8d resID=%s %r" % (o, r, t))

# 反向：CH 里含「三」的条目
print("\n### CH 含「三」的条目")
for o, r, s in ch:
    t = dec(s)
    if "三" in t:
        print("   @%-8d resID=%s %r" % (o, r, t[:60]))