# -*- coding: utf-8 -*-
# 解出 84F2.87ED 的英文原文（UTF-16LE），直接判定场景
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
vv = Vpp(VANILLA)
d = vv.read(vv.find("static_US", "le_strings"))
buckets, = struct.unpack_from("<H", d, 6)
count, = struct.unpack_from("<I", d, 8)
ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)


def us_rec(p):
    id1, id2 = struct.unpack_from("<HH", d, p)
    q = p + 4
    end = q
    while end + 1 < len(d):
        if d[end] == 0 and d[end + 1] == 0:
            break
        end += 2
    return id1, id2, d[q:end].decode("utf-16-le", "replace")


TARGETS = [(0x84F2, 0x87ED), (0x8858, 0x6942), (0x94CE, 0x7D20),
           (0x41A8, 0x4F70), (0x078C, 0x5E01), (0x723E, 0xD874)]
for i in range(count):
    p = ptrs[i]
    if p + 6 > len(d):
        continue
    a, b_, s = us_rec(p)
    if (a, b_) in TARGETS:
        print("[%04X.%04X] %s" % (a, b_, s))

# 顺带：找英文里同情境的（含 protect + homie/brother）
print("\n=== 含 'protect' 且短句（HUD 提示类）===")
n = 0
for i in range(count):
    p = ptrs[i]
    if p + 6 > len(d):
        continue
    a, b_, s = us_rec(p)
    if "protect" in s.lower() and len(s) < 60:
        print("  [%04X.%04X] %s" % (a, b_, s))
        n += 1
        if n >= 15:
            break
