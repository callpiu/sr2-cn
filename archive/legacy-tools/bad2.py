# -*- coding: utf-8 -*-
"""修正判据：slot < 0x20 视为控制字符（\n=10 等），不是越界。
   真正的越界 = slot >= 0x20 + len(table)。"""
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
LIM = 0x20 + len(cps)
CTRL = {10: "\\n", 13: "\\r", 9: "\\t"}


def dec(slots):
    out = []
    for s in slots:
        if s == 0:
            out.append("<NUL>"); continue
        if s < 0x20:
            out.append(CTRL.get(s, "<c%d>" % s)); continue
        i = s - 0x20
        out.append(chr(cps[i]) if i < len(cps) else "<OOB:%d>" % s)
    return "".join(out)


d = bytes(v.read(v.find("static_CH", "le_strings")))
b, c, off_at, offs = file_offsets(d)

oob_recs, texts = [], {}
for off in offs:
    r = read_units(d, off + 8)
    if not r or not r[0]:
        continue
    slots = [x for x, _ in r[0]]
    rid = struct.unpack_from("<HH", d, off)
    texts[off] = (rid, slots, dec(slots))
    if any(s >= LIM for s in slots):
        oob_recs.append((off, rid, [s for s in slots if s >= LIM], slots))

print("记录总数 %d   含越界 slot 的记录 %d" % (len(texts), len(oob_recs)))
for off, rid, o, slots in oob_recs:
    print("  @%-8d resID=(%5d,%5d) 越界slot=%s" % (off, rid[0], rid[1], o[:8]))
    print("      %r" % dec(slots)[:120])

print("\n### 现在全量搜索目标词")
for tg in ("辩护", "三王", "丈王", "律师", "指定"):
    hits = [(o, r, t) for o, (r, s, t) in texts.items() if tg in t]
    print("  [%s] %d 条" % (tg, len(hits)))
    for o, r, t in hits[:12]:
        print("     @%-8d %r" % (o, t[:80]))

print("\n### 控制字符使用统计（确认 \\n 用法）")
print("  含 slot10 的记录数:",
      sum(1 for r, s, t in texts.values() if 10 in s))
print("  含 slot<0x20 其他值的记录:",
      {k: sum(1 for r, s, t in texts.values() if k in s)
       for k in range(0, 0x20)})