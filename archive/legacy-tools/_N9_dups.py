# -*- coding: utf-8 -*-
"""查重：static_CH 里是否存在【重复 hash】的记录？

如果同一个 hash 有多条记录，我只改了第一条，
引擎可能读的是另一条（例如排序/覆盖关系）。
"""
import sys
import struct
import importlib.util
from collections import defaultdict

sys.path.insert(0, r"F:\sr2-cn")
from sr2font import Vpp

spec = importlib.util.spec_from_file_location('nf', r'F:\sr2-cn\_N6_buildtextfix.py')
nf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nf)

VPP = sys.argv[1] if len(sys.argv) > 1 else r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"
cl = nf.load_charlist(VPP)
v = Vpp(VPP)
d = bytearray(v.read(v.find("static_CH", "le_strings")))
recs, b_off, p_off, buckets, count = nf.le_strings_records(d)

print("=== static_CH 统计 ===")
print("  buckets=%d count=%d  解析出 %d 条" % (buckets, count, len(recs)))

byhash = defaultdict(list)
for i, (p, id1, id2, slots) in enumerate(recs):
    byhash[(id1 << 16) | id2].append((i, p, slots))

dups = {h: v for h, v in byhash.items() if len(v) > 1}
print("  不同 hash 数: %d" % len(byhash))
print("  重复 hash 数: %d" % len(dups))
print()

TARGETS = (0x84F287ED, 0x10AF1E62)
for h in TARGETS:
    lst = byhash.get(h, [])
    print("  目标 0x%08X: 共 %d 条记录" % (h, len(lst)))
    for (i, p, slots) in lst:
        t = "".join(chr(cl[s - 0x20]) if 0 <= s - 0x20 < len(cl) else "?" for s in slots)
        print("     #%d @0x%-8X (%d 槽位) = %s" % (i, p, len(slots), t))
    print()

# 检查 bucket 表：目标 hash 落在哪个 bucket
print("=" * 76)
print("bucket 表分析")
print("=" * 76)
for h in TARGETS:
    print("  目标 hash 0x%08X 的 bucket 分布:" % h)
    found = False
    for b in range(buckets):
        cnt, off = struct.unpack_from("<II", d, b_off + b * 8)
        if cnt == 0:
            continue
        # bucket 覆盖的记录范围
        member = []
        for (i, p, slots) in byhash.get(h, []):
            # 记录偏移在 ptr 数组里的位置
            for k in range(count):
                pp, = struct.unpack_from("<I", d, p_off + k * 4)
                if pp == p:
                    if off <= k < off + cnt:
                        member.append((b, cnt, off, k))
                    break
        if member:
            print("    bucket %d: count=%d offset=%d  -> %s" % (b, cnt, off, member))
            found = True
    if not found:
        print("    （未在 bucket 范围内找到，可能 offset 语义不同）")
    print()

# 打印 bucket 表头几项，理解语义
print("  bucket 表前 5 项 (count, offset):")
for b in range(5):
    cnt, off = struct.unpack_from("<II", d, b_off + b * 8)
    print("    [%d] count=%-5d offset=%-8d" % (b, cnt, off))
print()
print("  ptr 数组前 5 项:")
for k in range(5):
    pp, = struct.unpack_from("<I", d, p_off + k * 4)
    id1, id2 = struct.unpack_from("<HH", d, pp)
    print("    [%d] ptr=0x%-8X id=0x%04X%04X" % (k, pp, id1, id2))
