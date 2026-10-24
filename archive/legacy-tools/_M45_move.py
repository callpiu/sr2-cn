# -*- coding: utf-8 -*-
# 方案A 实施：搬 12 个字（的 兄 弟 需 出 去 几 生 意 免 遭 击）
# 每个字：从「正确格」复制 31x31 像素到「引擎实际取的格」
import sys, os, json, struct, shutil, hashlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp, dec_block, enc_block

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
SRC = os.path.join(G, "patch.vpp_pc")
BAK = r"F:/sr2-cn/_backup_GLYPH/patch.vpp_pc.before_glyphmove"
OUT = r"F:/sr2-cn/_FIX/patch_glyphmove.vpp_pc"
CELL = 31

plan = json.load(open(r"F:/sr2-cn/_glyphmove.json", encoding="utf-8"))
print("搬字形计划 %d 项" % len(plan))

f = Font(SRC)
B = [chr(c) for c in f.charlist]
atlas = bytearray(f.atlas)
BW = 2048 // 4

def px(A, X, Y):
    return dec_block(A, ((Y // 4) * BW + X // 4) * 16)[Y % 4][X % 4]

# 收集所有源格（避免写覆盖读）
srcs = {p["src"]: p for p in plan}
cache = {}
for k in srcs:
    ux, uy = f.uv(k)
    cache[k] = [[px(atlas, ux + xx, uy + yy) for xx in range(CELL)] for yy in range(CELL)]

log = []
for p in plan:
    c, dst, src = p["char"], p["dst"], p["src"]
    if src not in cache:
        ux, uy = f.uv(src)
        cache[src] = [[px(atlas, ux + xx, uy + yy) for xx in range(CELL)] for yy in range(CELL)]
    data = cache[src]
    vx, vy = f.uv(dst)
    for by in range(vy // 4, (vy + CELL - 1) // 4 + 1):
        for bx in range(vx // 4, (vx + CELL - 1) // 4 + 1):
            o = (by * BW + bx) * 16
            blk = [list(r) for r in dec_block(atlas, o)]
            for yy in range(4):
                Y = by * 4 + yy
                if not (vy <= Y < vy + CELL):
                    continue
                for xx in range(4):
                    X = bx * 4 + xx
                    if vx <= X < vx + CELL:
                        blk[yy][xx] = data[Y - vy][X - vx]
            atlas[o:o + 16] = enc_block(blk)
    log.append((c, src, dst, p["victim"], p["vfreq"]))

print("\n已搬:")
for c, s, d, v, vf in log:
    print("  格%-5d(%s的字形) -> 格%-5d(原装%s,%d次)  「%s」" % (s, c, d, v, vf, c))

# 写回
cn = Vpp(SRC)
raw = bytearray(open(SRC, "rb").read())
ae = cn.find("fnt_chinese", "g_peg_pc")
aoff = cn.abs_offset(ae)
raw[aoff:aoff + len(atlas)] = atlas

os.makedirs(os.path.dirname(BAK), exist_ok=True)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
if not os.path.exists(BAK):
    shutil.copy2(SRC, BAK)
    print("\n已备份 ->", BAK)
open(OUT, "wb").write(bytes(raw))
print("输出:", OUT, " md5=", hashlib.md5(bytes(raw)).hexdigest())

# 验证：导出被改格子的字形
f2 = Font(OUT)
import importlib
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import png_gray
items = []
for p in plan[:6]:
    k = p["dst"]
    ux, uy = f2.uv(k)
    items.append((k, [[px(f2.atlas, ux + xx, uy + yy)[3] for xx in range(CELL)] for yy in range(CELL)]))
SC, GAP, COLS = 6, 4, 6
SZ = CELL
w = COLS * (SZ * SC + GAP)
rows_n = (len(items) + COLS - 1) // COLS
h = rows_n * (SZ * SC + GAP)
cv = [[20] * w for _ in range(h)]
for n, (k, g) in enumerate(items):
    ox = (n % COLS) * (SZ * SC + GAP)
    oy = (n // COLS) * (SZ * SC + GAP)
    for yy in range(SZ):
        for xx in range(SZ):
            v = g[yy][xx]
            for dy in range(SC):
                for dx in range(SC):
                    cv[oy + yy * SC + dy][ox + xx * SC + dx] = v
png_gray(cv, 1, r"F:/sr2-cn/_glyphverify.png")
print("验证图 -> F:/sr2-cn/_glyphverify.png  顺序: %s" % " ".join(
    "%d=%s" % (p["dst"], p["char"]) for p in plan[:6]))
