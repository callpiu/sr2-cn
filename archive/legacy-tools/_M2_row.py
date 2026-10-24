# -*- coding: utf-8 -*-
"""输出图集某一行的所有格子（横向拼接），人工可读。

目的：验证「图集格 k 装的字形 = charlist[k+5]」这个前提。
如果成立，格 366 应该显示「你」、格 331 应该显示「任」。
"""
import os
import re
import struct
import sys

sys.path.insert(0, r"F:\sr2-cn")
from sr2font import Vpp, px_at, png_gray, CELL

OFFSET = 5


def load(vpp_path):
    v = Vpp(vpp_path)
    ae = v.find("fnt_chinese", "g_peg_pc")
    ve = v.find("fnt_chinese", "vf3_pc")
    ce = v.find("charlist_CH", "txt")
    atlas = v.read(ae)
    vf3 = v.read(ve)
    raw = v.read(ce)
    m = re.search(rb"count\s*=\s*(\d+)", raw)
    body = raw[m.end():] if m else raw
    end = body.find(b"//ENDOFFILE")
    cl = [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]
    N = struct.unpack_from("<I", vf3, 8)[0]
    UOFF = 0xD0 + N * 16
    VOFF = UOFF + N * 4

    def uv(k):
        return (struct.unpack_from("<i", vf3, UOFF + k * 4)[0],
                struct.unpack_from("<i", vf3, VOFF + k * 4)[0])
    return dict(atlas=atlas, cl=cl, N=N, uv=uv)


def main():
    vpp = sys.argv[1]
    kstart = int(sys.argv[2])
    kn = int(sys.argv[3])
    F = load(vpp)
    atlas, cl, uv, N = F["atlas"], F["cl"], F["uv"], F["N"]

    print("=== 输出格 %d..%d 横向拼接图 ===" % (kstart, kstart + kn - 1))
    cells = []
    labels = []
    for k in range(kstart, kstart + kn):
        if k >= N:
            break
        x, y = uv(k)
        cells.append([[px_at(atlas, x + xx, y + yy)[3] for xx in range(CELL)]
                      for yy in range(CELL)])
        j = k + OFFSET
        labels.append(chr(cl[j]) if j < len(cl) else "?")
    print("  格子对应的 charlist 字: %s" % "".join(labels))
    print()

    # 横向拼接一张图，scale=4
    scale = 4
    gap = 4
    W = kn * (CELL * scale + gap)
    H = CELL * scale + 40
    canvas = [[0] * W for _ in range(H)]
    for n, cell in enumerate(cells):
        px = n * (CELL * scale + gap)
        for yy in range(CELL * scale):
            for xx in range(CELL * scale):
                canvas[yy][px + xx] = cell[yy // scale][xx // scale]
    out = r"F:\sr2-cn\_row_%d_%d.png" % (kstart, kn)
    png_gray(canvas, 1, out)
    print("  已输出 %s" % out)
    print("  请肉眼核对：第 1 格 = 格 %d，应显示「%s」" % (kstart, labels[0]))


if __name__ == "__main__":
    main()
