# -*- coding: utf-8 -*-
"""终极判定测试：把字幕记录改成 ASCII 测试串。

结果解读
  屏幕出现 ASCII  -> 文字层通了，问题只在字形映射
  屏幕仍乱码      -> 引擎根本不读这条记录（文本另有来源）
"""
import sys
import re
import struct
import hashlib
import importlib.util

sys.path.insert(0, r"F:\sr2-cn")
from sr2font import Vpp

spec = importlib.util.spec_from_file_location('nf', r'F:\sr2-cn\_N6_buildtextfix.py')
nf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nf)

SRC = sys.argv[1]
DST = sys.argv[2]
TEXT1 = sys.argv[3] if len(sys.argv) > 3 else "AAABBBCCCDDDEEEFFFGGG"
TEXT2 = sys.argv[4] if len(sys.argv) > 4 else "HHHIIIJJJKKKLLLMMMNNNOOOPPP"

cl = nf.load_charlist(SRC)
IDX = {cp: i for i, cp in enumerate(cl)}
print("charlist: %d 项" % len(cl))

v = Vpp(SRC)
ent = v.find("static_CH", "le_strings")
abs_off = v.abs_offset(ent)
size = ent["size"]
raw = bytearray(open(SRC, "rb").read())
d = bytearray(raw[abs_off:abs_off + size])

recs, _, _, _, _ = nf.le_strings_records(d)
print("记录数: %d" % len(recs))
print()

TARGETS = (0x84F287ED, 0x10AF1E62)
texs = {0x84F287ED: TEXT1, 0x10AF1E62: TEXT2}
done = 0
for (p, id1, id2, slots) in recs:
    h = (id1 << 16) | id2
    if h not in TARGETS:
        continue
    t = texs[h]
    print("  0x%08X  %d 槽位 -> %s" % (h, len(slots), t))
    for j in range(len(slots)):
        ch = t[j] if j < len(t) else " "
        cp = ord(ch)
        # ASCII 的槽位就是码点本身
        s = cp if cp < 0x80 else (IDX.get(cp, 0x20) + 0x20)
        struct.pack_into(">H", d, p + 4 + j * 2, s)
    done += 1

raw[abs_off:abs_off + size] = d
open(DST, "wb").write(bytes(raw))
print()
print("已输出 %s (改 %d 条)" % (DST, done))
print("  md5 = %s" % hashlib.md5(open(DST, "rb").read()).hexdigest())

# 回读验证
d2 = bytearray(Vpp(DST).read(Vpp(DST).find("static_CH", "le_strings")))
recs2, _, _, _, _ = nf.le_strings_records(d2)
print()
print("回读验证:")
for (p, id1, id2, slots) in recs2:
    h = (id1 << 16) | id2
    if h in TARGETS:
        t = "".join(chr(s) if s < 0x80 else "?" for s in slots)
        print("  0x%08X = %s" % (h, t))
