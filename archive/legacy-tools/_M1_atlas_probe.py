# -*- coding: utf-8 -*-
"""从图集内容直接反推 M 表（引擎索引表）。

核心洞察
--------
文档已知：
    显示出来的字 = charlist_CH[ E(c) + OFFSET ]     (OFFSET = 5)
    图集第 k 格装的字形 = charlist_CH[ k + OFFSET ]

如果这两条同时成立，那 E(c) 就是「c 的字形在图集里的格子号」：
    字 c 的真实字形在 charlist 索引 i = index(c)
    -> 它装在格 k = i - OFFSET
    -> E(c) 应该 = k

但实测 E(你)=331、E(任)=331 有碰撞，说明 E(c) 不等于 i-OFFSET。
=> 「图集格子内容 = charlist[k+OFFSET]」这个前提可能是错的！

本脚本
    1. 直接解码图集，把所有格子渲染成一张对照图
    2. 检查格子 k 的内容是否真的等于 charlist[k+OFFSET] 的字形
    3. 尝试找出真正的关系

用法
    python _M1_atlas_probe.py <vpp路径> [起始格] [格数]
"""
import os
import re
import struct
import sys
import hashlib
import zlib

sys.path.insert(0, r"F:\sr2-cn")
from sr2font import Vpp, dec_block, px_at, png_gray, BW, CELL

OFFSET = 5


def load(vpp_path, atlas_name="fnt_chinese", atlas_ext="g_peg_pc"):
    v = Vpp(vpp_path)
    ae = v.find(atlas_name, atlas_ext)
    ve = v.find(atlas_name, "vf3_pc")
    ce = v.find("charlist_CH", "txt")
    if not (ae and ve and ce):
        raise SystemExit("缺少资源: atlas=%s vf3=%s charlist=%s" % (bool(ae), bool(ve), bool(ce)))
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

    return dict(v=v, atlas=atlas, vf3=vf3, cl=cl, N=N, UOFF=UOFF, VOFF=VOFF, uv=uv)


def cell_gray(atlas, x, y, size=CELL, pad=0):
    """取一个格子的灰度（用 alpha 通道）"""
    x -= pad
    y -= pad
    return [[px_at(atlas, x + xx, y + yy)[3] for xx in range(size)] for yy in range(size)]


def main():
    vpp = sys.argv[1] if len(sys.argv) > 1 else r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    count = int(sys.argv[3]) if len(sys.argv) > 3 else 60

    print("加载 %s" % vpp)
    F = load(vpp)
    print("  charlist = %d 项" % len(F["cl"]))
    print("  vf3 N = %d" % F["N"])
    print("  UOFF = 0x%X  VOFF = 0x%X  vf3 长度 = %d" % (F["UOFF"], F["VOFF"], len(F["vf3"])))
    print()

    # 1) 看看这些字的 vf3 索引和 charlist 索引
    print("=== 关键字的索引 ===")
    for ch in "你的弟兄们需要保护兄弟们正要去进行交易避免受到攻击":
        cp = ord(ch)
        i = F["cl"].index(cp) if cp in F["cl"] else None
        if i is not None:
            k = i - OFFSET
            uv = F["uv"](k) if 0 <= k < F["N"] else None
            print("  %s  charlist idx=%-5d  格 k=%-5d  UV=%s" % (ch, i, k, uv))
    print()

    # 2) 输出一批格子的对照图（人工确认格子内容）
    print("=== 输出格子 %d..%d 的对照图 ===" % (start, start + count - 1))
    cells = []
    for k in range(start, start + count):
        if k >= F["N"]:
            break
        x, y = F["uv"](k)
        cells.append(cell_gray(F["atlas"], x, y))
    out = r"F:\sr2-cn\_M_atlas_%d_%d.png" % (start, start + count)
    from sr2font import sheet
    sheet(cells, out, scale=3, cols=12)
    print("  已输出 %s (%d 格, 每格上方无标签，按行优先编号)" % (out, len(cells)))
    print()
    print("  格子 %d..%d 对应的 charlist 字 [k+%d]:" % (start, start + count - 1, OFFSET))
    line = []
    for k in range(start, min(start + count, F["N"])):
        j = k + OFFSET
        c = chr(F["cl"][j]) if j < len(F["cl"]) else "?"
        line.append("%s" % c)
    print("    " + "".join(line))


if __name__ == "__main__":
    main()
