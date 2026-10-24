# -*- coding: utf-8 -*-
"""1) 校准 static_US 的解码偏移（当前每条开头丢字符）
   2) 找出 CH 表缺失的 1602 条 US 条目里有什么
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


def load_raw(name, skip=0):
    d = bytes(v.read(v.find(name, "le_strings")))
    b, c, off_at, offs = file_offsets(d)
    out = []
    for off in offs:
        r = read_units(d, off + off + 4 + skip)   # off+8+skip
        if not r or not r[0]:
            continue
        slots = [x for x, _ in r[0]]
        rid = struct.unpack_from("<HH", d, off)
        out.append((off, rid, slots))
    return out


def dec(slots):
    return "".join(slot2ch.get(s, chr(s) if s < 0x20 else "\uFFFD") for s in slots)


print("### static_US 解码校准：尝试不同起始偏移")
for skip in (0, 1, 2, 3):
    us = load_raw("static_US", skip)
    txts = [dec(s) for _, _, s in us]
    # 统计可打印 ASCII 比例最高的偏移即正确
    ok = sum(1 for t in txts if t and all(ord(c) < 128 or c == "\uFFFD"
                                          for c in t))
    clean = sum(1 for t in txts if t and "\uFFFD" not in t)
    print("  skip=%d  无越界 %5d/%-5d 样例: %r"
          % (skip, clean, len(txts), (txts[8][:40] if len(txts) > 8 else "")))

SKIP = 2
us = load_raw("static_US", SKIP)
ch = load_raw("static_CH", 0)
print("\n采用 skip=%d" % SKIP)
print("  US 首 8 条:")
for off, rid, s in us[:8]:
    print("     @%-8d %r" % (off, dec(s)[:70]))

# resID 集合差异
us_ids = set(rid for _, rid, _ in us)
ch_ids = set(rid for _, rid, _ in ch)
print("\nUS 唯一 resID %d / CH %d" % (len(us_ids), len(ch_ids)))
only_us = us_ids - ch_ids
only_ch = ch_ids - us_ids
print("仅 US 有: %d仅 CH 有: %d" % (len(only_us), len(only_ch)))

usmap = {rid: dec(s) for _, rid, s in us}
miss = [usmap[r] for r in only_us if usmap[r]]
print("\n### 仅 US 有的条目里，含 King's / Three / Defender 等关键词")
kw = ("king", "three", "defender", "lawyer", "attorney", "tribunal")
hit = [t for t in miss if any(k in t.lower() for k in kw)]
for t in hit[:40]:
    print("   %r" % t[:90])
print("  命中 %d / %d" % (len(hit), len(miss)))

print("\n### 全部仅US 条目中最短 60 条（任务名通常很短）")
for t in sorted([t for t in miss if t], key=len)[:60]:
    print("   %r" % t[:70])