# -*- coding: utf-8 -*-
"""锁定 resID=(48647,14133) 这条 'e Kings' 的 CH 侧内容。
   同时用更宽的偏移扫描把 US 文本正确解出（不同记录长度不同，
   固定 skip 可能仍丢字 -> 逐条尝试多个起点取最长可打印结果）。"""
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

TARGET = (48647, 14133)


def dec(slots):
    return "".join(slot2ch.get(s, chr(s) if s < 0x20 else "\uFFFD")
                   for s in slots)


def load_best(name, starts=(0, 2, 4)):
    """对每条记录尝试多个起始偏移，选解码结果最可打印的。"""
    d = bytes(v.read(v.find(name, "le_strings")))
    b, c, off_at, offs = file_offsets(d)
    out = []
    for off in offs:
        best = None
        for sk in starts:
            r = read_units(d, off + 8 + sk)
            if not r or not r[0]:
                continue
            slots = [x for x, _ in r[0]]
            t = dec(slots)
            score = sum(1 for ch in t if 32 <= ord(ch) < 127)
            if best is None or score > best[0]:
                best = (score, t, slots, sk)
        if best:
            out.append((off, struct.unpack_from("<HH", d, off),
                        best[2], best[1], best[3]))
    return out


print("### 用最优偏移重解 static_US，锁定 Kings 相关")
us = load_best("static_US")
ch = load_best("static_CH")
print("US %d / CH %d\n" % (len(us), len(ch)))

ch_by_id = {}
for o, r, s, t, sk in ch:
    ch_by_id.setdefault(r, (o, t, s))

print("### resID=%s 的两侧内容" % (TARGET,))
for o, r, s, t, sk in us:
    if r == TARGET:
        print("  US @%-8d skip=%d %r" % (o, sk, t))
        print("     slots=%s" % s[:30])
c = ch_by_id.get(TARGET)
print("  CH -> %r" % (c[1] if c else "【不存在】"))

print("\n### US 里所有 'Kings' 完整条目 + CH 对应")
for o, r, s, t, sk in us:
    if "kings" in t.lower() and len(t) < 60:
        c = ch_by_id.get(r)
        print("  US @%-8d %-32r  CH=%r"
              % (o, t[:32], c[1][:24] if c else None))

print("\n### US 里 'Three' 完整短条目 + CH 对应")
for o, r, s, t, sk in us:
    if "three" in t.lower() and len(t) < 50:
        c = ch_by_id.get(r)
        print("  US @%-8d %-32r  CH=%r"
              % (o, t[:32], c[1][:24] if c else None))