# -*- coding: utf-8 -*-
"""裁出「引擎实际会画出的格子」并输出 PNG —— 图形直接判定。

对记录里的每个槽位 s：
    引擎会画图集第 k = M(c) - 5 格
    而 s = charlist.index(c) + 0x20  =>  charlist.index(c) = s - 0x20
    如果 M(c) == charlist.index(c)，引擎画的格 k = s - 0x20
    如果引擎画的格 = s - 0x20，那格子里装的是 charlist[k+5] = c 本身

本脚本
    1. 从图集裁出格 (s-0x20) 的字形，横向拼接 -> 这就是「引擎实际会画出来的字」
    2. 同时裁出格 (s-0x20) 附近 + 也裁出候选
    3. 输出 PNG，肉眼一读就知道
"""
import sys
import importlib.util

sys.path.insert(0, r"F:\sr2-cn")
from sr2font import Vpp, px_at, png_gray, CELL

spec = importlib.util.spec_from_file_location('nf', r'F:\sr2-cn\_N6_buildtextfix.py')
nf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nf)

OFFSET = 5
VPP = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else r"F:\sr2-cn\_engine_would_draw.png"


def load_atlas_and_vf3(vpp_path):
    v = Vpp(vpp_path)
    atlas = v.read(v.find("fnt_chinese", "g_peg_pc"))
    vf3 = v.read(v.find("fnt_chinese", "vf3_pc"))
    import struct
    N, = struct.unpack_from("<I", vf3, 8)
    UOFF = 0xD0 + N * 16
    VOFF = UOFF + N * 4

    def uv(k):
        return (struct.unpack_from("<i", vf3, UOFF + k * 4)[0],
                struct.unpack_from("<i", vf3, VOFF + k * 4)[0])
    return atlas, uv, N


cl = nf.load_charlist(VPP)
IDX = {cp: i for i, cp in enumerate(cl)}
atlas, uv, N = load_atlas_and_vf3(VPP)

v = Vpp(VPP)
d = bytearray(v.read(v.find("static_CH", "le_strings")))
recs, _, _, _, _ = nf.le_strings_records(d)

for (p, id1, id2, slots) in recs:
    h = (id1 << 16) | id2
    if h not in (0x84F287ED, 0x10AF1E62):
        continue

    # 记录里的字（按 charlist 解码）
    chars = [chr(cl[s - 0x20]) if 0 <= s - 0x20 < len(cl) else "?" for s in slots]
    print("记录 0x%08X" % h)
    print("  按 charlist 解码: %s" % "".join(chars))
    print("  槽位: %s" % slots[:24])
    print()

    # 引擎会画的格：如果 M(c) == charlist.index(c)，则 k = s - 0x20
    cells = []
    labels = []
    for s in slots:
        k = s - 0x20
        if k < 0 or k >= N:
            cells.append([[0] * CELL for _ in range(CELL)])
            labels.append("?")
            continue
        x, y = uv(k)
        cells.append([[px_at(atlas, x + xx, y + yy)[3] for xx in range(CELL)]
                      for yy in range(CELL)])
        j = k + OFFSET
        labels.append(chr(cl[j]) if j < len(cl) else "?")
    print("  引擎画的格 k = s-0x20，这些格【装】的字: %s" % "".join(labels))
    print()

    # 拼接输出
    scale = 4
    gap = 4
    n = len(cells)
    cols = 24
    rowsn = (n + cols - 1) // cols
    cw = CELL * scale
    W = cols * (cw + gap)
    H = rowsn * (cw + gap)
    canvas = [[18] * W for _ in range(H)]
    for i, c in enumerate(cells):
        px = (i % cols) * (cw + gap)
        py = (i // cols) * (cw + gap)
        for yy in range(cw):
            for xx in range(cw):
                canvas[py + yy][px + xx] = c[yy // scale][xx // scale]
    out = OUT.replace(".png", "_%08X.png" % h)
    png_gray(canvas, 1, out)
    print("  已输出 %s" % out)
    print("  ^ 这张图就是【引擎实际会画出来的字】，照着读一遍即可确认")
    print()
