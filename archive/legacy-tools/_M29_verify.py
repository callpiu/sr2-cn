# -*- coding: utf-8 -*-
# 验证修复文件：1) 位 已清除  2) 图集357格=们  3) 结构完好
import sys, struct, os
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp, dec_block, enc_block

OUT = r"F:/sr2-cn/_FIX/patch_weifix.vpp_pc"
SRC = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"

cn = Vpp(OUT)
f = Font(OUT)
B = [chr(c) for c in f.charlist]
print("新文件 charlist =", len(B), " N =", f.N)


def load(name):
    d = cn.read(cn.find(name, "le_strings"))
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    return d, count, ptrs


def rec(d, p):
    id1, id2 = struct.unpack_from("<HH", d, p)
    q = p + 4
    out = []
    while True:
        s, = struct.unpack_from(">H", d, q)
        q += 2
        if s == 0:
            break
        k = s - 32
        out.append(B[k] if 0 <= k < len(B) else "{%d}" % s)
    return id1, id2, "".join(out)


print("\n=== 1) 位 的残留 ===")
tot = 0
for name in ("voice_script_CH", "static_CH", "platform_pc_CH"):
    d, count, ptrs = load(name)
    n = 0
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d):
            continue
        try:
            _, _, t = rec(d, p)
        except Exception:
            continue
        n += t.count("位")
    print("  %-18s 残留「位」= %d" % (name, n))
    tot += n
print("  合计残留 =", tot)

print("\n=== 2) 关键句验证 ===")
for name in ("static_CH", "voice_script_CH"):
    d, count, ptrs = load(name)
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d):
            continue
        try:
            a, b_, t = rec(d, p)
        except Exception:
            continue
        if (a, b_) == (0x84F2, 0x87ED):
            print("  ★ [84F2.87ED] %s" % t)

print("\n=== 3) 图集第357格 vs 第327格（应完全相同）===")
CELL = 31


def cell(A, k):
    x, y = f.uv(k)
    return [[dec_block(A, ((y + yy) // 4 * 512 + (x + xx) // 4) * 16)[(y + yy) % 4][(x + xx) % 4]
             for xx in range(CELL)] for yy in range(CELL)]


at = f.atlas
c357, c327 = cell(at, 357), cell(at, 327)
same = all(c357[y][x] == c327[y][x] for y in range(CELL) for x in range(CELL))
print("  第357格 == 第327格 :", same)

# 与原文件对比：第327格未变，第357格已变
fold = Font(SRC)
c357_old = cell(fold.atlas, 357)
diff = sum(1 for y in range(CELL) for x in range(CELL) if c357[y][x] != c357_old[y][x])
print("  第357格与原文件差异像素 = %d / %d" % (diff, CELL * CELL))
c327_old = cell(fold.atlas, 327)
same327 = all(c327[y][x] == c327_old[y][x] for y in range(CELL) for x in range(CELL))
print("  第327格（们 原格）未变 :", same327)

# 4) 结构校验：count/buckets 与原文件一致
for name in ("voice_script_CH", "static_CH", "platform_pc_CH"):
    do, co, _ = load(name)
    cn2 = Vpp(SRC)
    d2 = cn2.read(cn2.find(name, "le_strings"))
    bo, = struct.unpack_from("<H", do, 6)
    b2, = struct.unpack_from("<H", d2, 6)
    print("  %-18s buckets %d/%d  count %d/%d  大小 %d/%d" % (
        name, bo, b2, co, struct.unpack_from("<I", d2, 8)[0], len(do), len(d2)))
