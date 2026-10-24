# -*- coding: utf-8 -*-
"""1) static_US 里英文原名是什么
   2) 三王/Three Kings 相关记录在CH 侧的对应条目
   3) 用 record 的 resourceID 去 static_US 找同一ID，看官方怎么写的"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in
       v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]


def dec(slots, table):
    out = []
    for s in slots:
        idx = s - 0x20
        out.append(chr(table[idx]) if 0 <= idx < len(table) else None)
    return None if any(c is None for c in out) else "".join(out)


def collect(name, table):
    d = bytes(v.read(v.find(name, "le_strings")))
    b, c, off_at, offs = file_offsets(d)
    out = {}
    for off in offs:
        r = read_units(d, off + 8)
        if not r or not r[0]:
            continue
        slots = [x for x, _ in r[0]]
        t = dec(slots, table)
        if t is None:
            continue
        rid = struct.unpack_from("<HH", d, off)
        out[off] = (rid, t, slots)
    return out


print("### static_US 条目数")
us = {}
d = bytes(v.read(v.find("static_US", "le_strings")))
b, c, off_at, offs = file_offsets(d)
usmap = {}
for off in offs:
    r = read_units(d, off + 8)
    if not r or not r[0]:
        continue
    slots = [x for x, _ in r[0]]
    t = dec(slots, cps)          # US 文件的 slot 也按 CH 表试解
    rid = struct.unpack_from("<HH", d, off)
    usmap[off] = (rid, t, slots)
print("  可解码 %d / %d" % (len(usmap), len(offs)))

print("\n### 在 static_US(按 CH 表解) 搜 '律师' '辩护' 相关英文")
for off, (rid, t, slots) in usmap.items():
    if t and ("辩护" in t or "三王" in t or "丈" in t):
        print("   @%-8d %r" % (off, t))

print("\n### 关键：CH 侧两条记录的 resourceID，在 US 侧同ID 是什么")
ch = collect("static_CH", cps)
for off in (225978, 279274):
    rid, t, slots = ch[off]
    print("  CH @%d resID=(%d,%d) %r" % (off, rid[0], rid[1], t))
    # US 表里找相同 resID
    found = [(uo, ut) for uo, (ur, ut, us_) in usmap.items() if ur == rid]
    for uo, ut in found[:3]:
        print("      US 同ID @%-8d %r" % (uo, ut))
    if not found:
        print("      US 表里无同 resID 记录")

print("\n### CH 表里所有含 '王' 的短条目(<6字)")
for off, (rid, t, slots) in sorted(ch.items()):
    if t and "王" in t and len(t) <= 6:
        print("   @%-8d %r" % (off, t))