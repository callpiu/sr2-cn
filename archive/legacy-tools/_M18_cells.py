# -*- coding: utf-8 -*-
# 决定性检验：图集第 332/362/1190/2342 格实际装的是什么字形
# 若第332格不是「们」而是「位」-> 图集打包错位（与字符表无关）
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, png_gray, sheet

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
f = Font(CN)
B = [chr(c) for c in f.charlist]
CELL = 31
PAD = 3
SZ = CELL + PAD * 2


def cell_gray(k):
    x, y = f.uv(k)
    x -= PAD
    y -= PAD
    return [[px_at(f.atlas, x + xx, y + yy)[3] for xx in range(SZ)] for yy in range(SZ)]


def px_at(atlas, X, Y):
    return dec_block(atlas, ((Y // 4) * 2048 // 4 + X // 4) * 16)[Y % 4][X % 4]


def dec_block(buf, off):
    b = buf[off:off + 16]
    c0 = b[8] | (b[9] << 8)
    c1 = b[10] | (b[11] << 8)
    idx = int.from_bytes(bytes(b[12:16]), "little")

    def rgb(v):
        return (((v >> 11) & 0x1F) * 255 // 31, ((v >> 5) & 0x3F) * 255 // 63, (v & 0x1F) * 255 // 31)
    p0, p1 = rgb(c0), rgb(c1)
    if c0 > c1:
        pal = [p0, p1, tuple((2 * p0[i] + p1[i]) // 3 for i in range(3)),
               tuple((p0[i] + 2 * p1[i]) // 3 for i in range(3))]
    else:
        pal = [p0, p1, tuple((p0[i] + p1[i]) // 2 for i in range(3)), (0, 0, 0)]
    out = []
    for py in range(4):
        row = []
        for px_ in range(4):
            k = py * 4 + px_
            a4 = (b[k // 2] >> (4 * (k % 2))) & 0xF
            r, g, bl = pal[(idx >> (2 * k)) & 3]
            row.append((r, g, bl, a4 * 17))
        out.append(row)
    return out


from sr2font import dec_block as _db  # noqa

# 目标格子：B 中 们=332 位=362 护=1190 该=2342
targets = [(332, "B[332]=们"), (362, "B[362]=位"), (1190, "B[1190]=护"), (2342, "B[2342]=该")]

# 每格放大 6x，4 格一行，带编号
SC = 6
GAP = 2
COLS = 4
w = COLS * (SZ * SC + GAP)
rows_n = (len(targets) + COLS - 1) // COLS
h = rows_n * (SZ * SC + GAP)
canvas = [[25] * w for _ in range(h)]
for n, (k, label) in enumerate(targets):
    g = cell_gray(k)
    ox = (n % COLS) * (SZ * SC + GAP)
    oy = (n // COLS) * (SZ * SC + GAP)
    for yy in range(SZ):
        for xx in range(SZ):
            v = g[yy][xx]
            for dy in range(SC):
                for dx in range(SC):
                    canvas[oy + yy * SC + dy][ox + xx * SC + dx] = v
png_gray(canvas, 1, r"F:/sr2-cn/_cells_key.png")
print("输出 F:/sr2-cn/_cells_key.png  顺序: %s" % [t[1] for t in targets])

# 同时导出更大的范围：们(332) 前后各 20 格，看整个区段
span = 20
cells = []
ks = list(range(332 - span, 332 + span + 1))
for k in ks:
    cells.append(cell_gray(k))
sheet(cells, r"F:/sr2-cn/_cells_men.png")
print("输出 F:/sr2-cn/_cells_men.png  格子 %d..%d（们=332 应在此范围中部）" % (ks[0], ks[-1]))

cells = []
ks = list(range(1190 - span, 1190 + span + 1))
for k in ks:
    cells.append(cell_gray(k))
sheet(cells, r"F:/sr2-cn/_cells_hu.png")
print("输出 F:/sr2-cn/_cells_hu.png  格子 %d..%d（护=1190 应在此范围中部）" % (ks[0], ks[-1]))
