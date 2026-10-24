# -*- coding: utf-8 -*-
# 完整英文 + 定位引用方：tutorial.lua 是否引用 8858.6942
import sys, struct, os, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

vv = Vpp(VANILLA)
d_us = vv.read(vv.find("static_US", "le_strings"))
buckets_us, = struct.unpack_from("<H", d_us, 6)
count_us, = struct.unpack_from("<I", d_us, 8)
ptrs_us = struct.unpack_from("<%dI" % count_us, d_us, 12 + buckets_us * 8)


def us_rec(p):
    id1, id2 = struct.unpack_from("<HH", d_us, p)
    q = p + 4
    end = q
    while end + 1 < len(d_us):
        if d_us[end] == 0 and d_us[end + 1] == 0:
            break
        end += 2
    return id1, id2, d_us[q:end].decode("utf-16-le", "replace")


# 1) 完整英文
for i in range(count_us):
    p = ptrs_us[i]
    if p + 6 > len(d_us):
        continue
    a, b_, s = us_rec(p)
    if (a, b_) == (0x8858, 0x6942):
        print("★ [8858.6942] 英文原文 = %r" % s)

# 2) 所有含 standing around 的（确认是否是通用催促）
print("\n=== 含 'standing around' 的英文记录 ===")
for i in range(count_us):
    p = ptrs_us[i]
    if p + 6 > len(d_us):
        continue
    a, b_, s = us_rec(p)
    if "standing around" in s.lower():
        print("  [%04X.%04X] %s" % (a, b_, s))

# 3) 在游戏文件里搜这个 hash 的引用（lua 常用 'name' 或 hash）
print("\n=== 搜 8858.6942 的引用（lua/xtbl/txt）===")
needle = bytes([0x58, 0x88, 0x42, 0x69])
needle2 = bytes([0x88, 0x58, 0x69, 0x42])
hits = []
for root, dirs, files in os.walk(G):
    if any(x in root.lower() for x in ("_backup", "pdb", ".venv", "sr2-cn")):
        continue
    for fn in files:
        if not fn.lower().endswith((".lua", ".xtbl", ".txt", ".cxt", ".lt2", ".tbl")):
            continue
        p = os.path.join(root, fn)
        try:
            with open(p, "rb") as f:
                data = f.read()
        except Exception:
            continue
        if needle in data or needle2 in data:
            hits.append((p, data.count(needle) + data.count(needle2)))
for p, c in hits[:30]:
    print("  %s  x%d" % (p.replace(G + os.sep, ""), c))
if not hits:
    print("  (无直接引用)")

# 4) 教程提示集合：static_CH 里含「记住：」的
cn = Vpp(os.path.join(G, "patch.vpp_pc"))
d_cn = cn.read(cn.find("static_CH", "le_strings"))
buckets_cn, = struct.unpack_from("<H", d_cn, 6)
count_cn, = struct.unpack_from("<I", d_cn, 8)
ptrs_cn = struct.unpack_from("<%dI" % count_cn, d_cn, 12 + buckets_cn * 8)
from sr2font import Font
f = Font(os.path.join(G, "patch.vpp_pc"))
B = [chr(c) for c in f.charlist]


def cn_rec(p):
    id1, id2 = struct.unpack_from("<HH", d_cn, p)
    q = p + 4
    out = []
    while True:
        s, = struct.unpack_from(">H", d_cn, q)
        q += 2
        if s == 0:
            break
        i = s - 32
        out.append(B[i] if 0 <= i < len(B) else "{%d}" % s)
    return id1, id2, "".join(out)


print("\n=== static_CH 教程类提示（含『记住：』）===")
n = 0
for i in range(count_cn):
    p = ptrs_cn[i]
    if p + 6 > len(d_cn):
        continue
    a, b_, t = cn_rec(p)
    if "记住：" in t:
        print("  [%04X.%04X] %s" % (a, b_, t[:70]))
        n += 1
        if n >= 12:
            break
