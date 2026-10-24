# -*- coding: utf-8 -*-
"""用内部任务标识 SAINTS2 / SAINTS4 反查字符串表。
   同时检查：是否存在与「辩护律师」同 resID 的重复记录。"""
import sys, os, struct, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
sys.stdout.reconfigure(encoding="utf-8")
from collections import defaultdict

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in
       v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
slot2ch = {i + 0x20: chr(c) for i, c in enumerate(cps)}


def dec(s):
    return "".join(slot2ch.get(x, chr(x) if x < 0x20 else "?") for x in s)


def load(name, skip=0):
    d = bytes(v.read(v.find(name, "le_strings")))
    b, c, off_at, offs = file_offsets(d)
    out = []
    for off in offs:
        r = read_units(d, off + 8 + skip)
        if not r or not r[0]:
            continue
        out.append((off, struct.unpack_from("<HH", d, off),
                    [x for x, _ in r[0]]))
    return d, out


print("### 1. 全资源搜 ASCII 'SAINTS2' / 'SAINTS4'")
for key in (b"SAINTS2", b"SAINTS4", b"saints2", b"saints4"):
    hits = []
    for en in v.entries():
        if en["size"] > 3_000_000:
            continue
        try:
            d = bytes(v.read(v.find(en["name"], en["ext"])))
        except Exception:
            continue
        if key in d:
            hits.append((en["name"], en["ext"], d.count(key)))
    print("  %-10s -> %s" % (key.decode(),
          ", ".join("%s.%s x%d" % h for h in hits) or "无"))

print("\n### 2. static_US 中Appointed Defender / Three Kings 完整解码")
du, us = load("static_US", 0)
# US 表的slot 是 ASCII 码点（英文版 slot=ASCII），直接按 chr 解
def dec_us(s):
    return "".join(chr(x) if 32 <= x < 127 else
                   {10: "\\n", 13: "\\r", 9: "\\t"}.get(x, "") for x in s)

# 尝试多个起始偏移，取能解出目标词的那个
for skip in range(0, 6):
    dd, rows = load("static_US", skip)
    got = []
    for off, rid, s in rows:
        t = dec_us(s)
        if "Appointed Defender" in t or "Three Kings" in t:
            got.append((off, rid, t))
    if got:
        print("  skip=%d 命中 %d 条:" % (skip, len(got)))
        for o, r, t in got:
            print("     @%-8d resID=%s %r" % (o, r, t[:60]))
        US_SKIP = skip
        break
else:
    US_SKIP = None
    print("  所有偏移都未命中")

print("\n### 3. static_CH 中所有 resID 重复的记录（找「辩护律师」的竞争者）")
dch, ch = load("static_CH", 0)
byid = defaultdict(list)
for off, rid, s in ch:
    byid[rid].append((off, s))
dups = {k: v2 for k, v2 in byid.items() if len(v2) > 1}
print("  CH 共 %d 条,唯一 resID %d, 重复 resID %d 个"
      % (len(ch), len(byid), len(dups)))

LAWYER_ID = (55501, 33317)
print("\n  resID=%s 的全部记录:" % (LAWYER_ID,))
for off, s in byid.get(LAWYER_ID, []):
    print("     @%-8d %rslots=%s" % (off, dec(s), s))

print("\n### 4. 槽位层面：是否存在 [2506,1222,X,1013] 任意 X")
target = [2506, 1222, 1013]
for off, rid, s in ch:
    for i in range(len(s) - 3):
        if s[i] == 2506 and s[i + 1] == 1222 and s[i + 3] == 1013:
            print("   @%-8d %r  slots=%s" % (off, dec(s), s[max(0, i - 2):i + 6]))

print("\n### 5. 槽位层面：是否存在 [X,1796] 且 X 在三/丈 邻近")
for off, rid, s in ch:
    for i in range(len(s) - 1):
        if s[i + 1] == 1796 and 265 <= s[i] <= 275:
            print("   @%-8d %r  slots=%s" % (off, dec(s), s))