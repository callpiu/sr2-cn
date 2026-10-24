# -*- coding: utf-8 -*-
# 用英文原版解出 8858.6942 的英文原文，据此判断它属于什么情境/任务
import sys, struct, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"


def load_us():
    """static_US 英文表（ASCII，不需要 charlist）"""
    v = Vpp(VANILLA)
    e = v.find("static_US", "le_strings")
    d = v.read(e)
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    return d, count, ptrs


def rec_us(d, p):
    """英文表：id1/id2 后是 ASCII 字符串，0 结尾"""
    id1, id2 = struct.unpack_from("<HH", d, p)
    q = p + 4
    end = d.find(b"\x00", q)
    s = d[q:end]
    return id1, id2, s


d, count, ptrs = load_us()
print("static_US count =", count)

TARGETS = [(0x8858, 0x6942)]
found = {}
for i in range(count):
    p = ptrs[i]
    if p + 6 > len(d):
        continue
    id1, id2, s = rec_us(d, p)
    if (id1, id2) in TARGETS:
        found[(id1, id2)] = s
        print("★ [%04X.%04X] = %r" % (id1, id2, s))

# 搜同情境的英文：含 "standing" / "move" / "hurry" 的短提示
print("\n=== 英文表里相关情境提示（含 standing/move it/hurry）===")
pat = re.compile(rb"standing|move it|hurry|get moving|idiot|still", re.I)
n = 0
for i in range(count):
    p = ptrs[i]
    if p + 6 > len(d):
        continue
    id1, id2, s = rec_us(d, p)
    if pat.search(s) and len(s) < 90:
        print("  [%04X.%04X] %s" % (id1, id2, s.decode("ascii", "replace")))
        n += 1
        if n >= 15:
            break

# 关键：8858.6942 的邻居记录（同 id1 前缀的英文任务提示）
print("\n=== id1 邻近的英文 static 记录（0x8858±0x20）===")
for i in range(count):
    p = ptrs[i]
    if p + 6 > len(d):
        continue
    id1, id2, s = rec_us(d, p)
    if abs(id1 - 0x8858) <= 0x20 and 0 < len(s) < 80:
        print("  [%04X.%04X] %s" % (id1, id2, s.decode("ascii", "replace")))
