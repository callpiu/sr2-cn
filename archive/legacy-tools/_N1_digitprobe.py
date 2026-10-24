# -*- coding: utf-8 -*-
"""探针生成器：把「索引数字」直接画进图集格子，一张截图读出整段 E 表。

原理
    图集格 k 装的字形 = charlist[k+5]（已视觉验证）
    如果我把格 k 的图案换成「k 的十进制数字」，
    那么当某个字符 c 显示出来时，屏幕上出现的就是 E(c) 的数值 ——
    一张截图就能读出整段映射，不需要认字！

用法
    # 1) 生成探针 vpp（把某个区间的格子换成数字图）
    python _N1_digitprobe.py make <vpp> <k_start> <k_end> <out_vpp>

    # 2) 把字幕记录改成候选字序列
    python _N1_digitprobe.py text <vpp> <chars> <out_vpp>
"""
import os
import re
import struct
import sys
import json

sys.path.insert(0, r"F:\sr2-cn")
from sr2font import Vpp, dec_block, enc_block, px_at, BW, CELL

OFFSET = 5

# ---------------------------------------------------------------- 5x7 点阵字体
FONT = {
    '0': ["01110","10001","10011","10101","11001","10001","01110"],
    '1': ["00100","01100","00100","00100","00100","00100","01110"],
    '2': ["01110","10001","00001","00010","00100","01000","11111"],
    '3': ["11111","00010","00100","00010","00001","10001","01110"],
    '4': ["00010","00110","01010","10010","11111","00010","00010"],
    '5': ["11111","10000","11110","00001","00001","10001","01110"],
    '6': ["00110","01000","10000","11110","10001","10001","01110"],
    '7': ["11111","00001","00010","00100","01000","01000","01000"],
    '8': ["01110","10001","10001","01110","10001","10001","01110"],
    '9': ["01110","10001","10001","01111","00001","00010","01100"],
    '#': ["01010","11111","01010","01010","01010","11111","01010"],
    '-': ["00000","00000","00000","11111","00000","00000","00000"],
}


def draw_number(cell, text, y0=8, scale=2):
    """把 text 画进 CELL×CELL 的灰度格子里"""
    x = 2
    for ch in text:
        g = FONT.get(ch)
        if not g:
            continue
        for ry in range(7):
            for rx in range(5):
                if g[ry][rx] == '1':
                    for sy in range(scale):
                        for sx in range(scale):
                            Y = y0 + ry * scale + sy
                            X = x + rx * scale + sx
                            if 0 <= Y < CELL and 0 <= X < CELL:
                                cell[Y][X] = 255
        x += 5 * scale + scale


def write_cell(atlas, out, uv, k, cell):
    """把格子写回图集（只重编受影响的 DXT3 块）"""
    ux, vy = uv(k)
    for by in range(vy // 4, (vy + CELL - 1) // 4 + 1):
        for bx in range(ux // 4, (ux + CELL - 1) // 4 + 1):
            o = (by * BW + bx) * 16
            blk = [list(r) for r in dec_block(atlas, o)]
            for yy in range(4):
                Y = by * 4 + yy
                if not (vy <= Y < vy + CELL):
                    continue
                for xx in range(4):
                    X = bx * 4 + xx
                    if ux <= X < ux + CELL:
                        v = cell[Y - vy][X - ux]
                        blk[yy][xx] = (v, v, v, v)
            out[o:o + 16] = enc_block(blk)


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
    return dict(v=v, atlas=atlas, cl=cl, N=N, uv=uv, ae=ae)


def cmd_make(vpp, k0, k1, out_vpp):
    F = load(vpp)
    atlas = bytearray(F["atlas"])
    n = 0
    for k in range(k0, min(k1, F["N"])):
        cell = [[0] * CELL for _ in range(CELL)]
        draw_number(cell, str(k))
        write_cell(F["atlas"], atlas, F["uv"], k, cell)
        n += 1
    # 保存
    v = F["v"]
    off = v.abs_offset(F["ae"])
    v.data[off:off + len(F["atlas"])] = bytes(atlas)
    open(out_vpp, "wb").write(bytes(v.data))
    print("已生成探针 vpp: %s" % out_vpp)
    print("  格 %d..%d 已换成数字图（共 %d 格）" % (k0, min(k1, F["N"]) - 1, n))
    print("  对应 charlist 索引 %d..%d" % (k0 + OFFSET, min(k1, F["N"]) - 1 + OFFSET))
    print()
    print("  这些格对应的字:")
    for k in range(k0, min(k1, F["N"])):
        j = k + OFFSET
        if j < len(F["cl"]):
            print("    格 %-5d (charlist idx %-5d) = %s" % (k, j, chr(F["cl"][j])))


def cmd_text(vpp, chars, out_vpp):
    """把 static_CH 的两条字幕记录改成给定字符序列"""
    F = load(vpp)
    IDX = {cp: i for i, cp in enumerate(F["cl"])}
    import sys as _s
    sys.path.insert(0, r"F:\sr2-cn\pylibs")
    from sr2lib import Vpp as V2
    from sr2patch import file_offsets, read_units

    path = vpp
    v2 = V2(path)
    ent = v2.find("static_CH", "le_strings")
    body = bytes(v2.read(ent))
    raw = bytearray(open(path, "rb").read())
    pos = raw.find(body)
    if pos < 0:
        raise SystemExit("无法定位 static_CH")
    d = bytearray(body)
    b, c, oa, offs = file_offsets(bytes(d))

    TARGETS = (0x84F287ED, 0x10AF1E62)
    slots = [IDX[ord(ch)] + 0x20 for ch in chars if ord(ch) in IDX]
    missing = [ch for ch in chars if ord(ch) not in IDX]
    if missing:
        print("  警告：这些字不在 charlist: %s" % "".join(missing))
    print("  目标字符: %s" % chars)
    print("  槽位: %s" % slots[:20])

    done = 0
    for off in [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]:
        id1, id2 = struct.unpack_from("<HH", d, off)
        h = (id1 << 16) | id2
        if h not in TARGETS:
            continue
        u, _ = read_units(bytes(d), off + 8)
        old = [x for x, _ in u]
        new = slots[:len(old)] + [0x20] * max(0, len(old) - len(slots))
        for j, s in enumerate(new[:len(old)]):
            bp = off + 8 + j * 2
            d[bp] = (s >> 8) & 0xFF
            d[bp + 1] = s & 0xFF
        print("  0x%08X: %d 槽位 -> 已改" % (h, len(old)))
        done += 1

    raw[pos:pos + len(d)] = d
    open(out_vpp, "wb").write(bytes(raw))
    print("  已输出 %s (%d 条记录)" % (out_vpp, done))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "make":
        cmd_make(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    elif cmd == "text":
        cmd_text(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print(__doc__)
