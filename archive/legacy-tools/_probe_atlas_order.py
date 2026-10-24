# -*- coding: utf-8 -*-
"""用标准字体模板匹配，判定哪张图集的字形顺序 = charlist。
对每个字 c（charlist 索引 k），把图集在 uv(k-8..k+8) 的格子与渲染出的 c 比对，
最佳匹配的相对偏移 j-k 若恒为 0，则该图集顺序正确。"""
import sys, struct, os
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp, dec_block, BW
from PIL import Image, ImageFont, ImageDraw

V10 = r"F:/sr2-cn/SR2_简体中文补丁_v10_20261014"
VF3_SRC = V10 + "/common.vpp_pc"
ATLASES = {
    "official": (V10 + "/backup_original/patch.vpp_pc", "g_peg_pc"),
    "v10patch": (V10 + "/patch.vpp_pc", "g_peg_pc"),
    "textures": (r"G:/SteamLibrary/steamapps/common/Saints Row 2/textures.vpp_pc", None),
}

def load_vf3(path):
    v = Vpp(path); e = v.find("fnt_chinese", "vf3_pc"); return v.read(e)
def load_charlist(path):
    v = Vpp(path); e = v.find("charlist_CH", "txt")
    import re
    raw = v.read(e); m = re.search(rb"count\s*=\s*(\d+)", raw)
    body = raw[m.end():] if m else raw
    end = body.find(b"//ENDOFFILE")
    return [int(x) for x in re.findall(rb"\d+", body[:end if end > 0 else None])]
def load_atlas(path, ext):
    v = Vpp(path)
    e = v.find("fnt_chinese", ext) if ext else v.find("fnt_chinese")
    return v.read(e)

vf3 = load_vf3(VF3_SRC)
N = struct.unpack_from("<I", vf3, 8)[0]
UOFF = 0xD0 + N * 16; VOFF = UOFF + N * 4
def uv(k):
    return (struct.unpack_from("<i", vf3, UOFF + k * 4)[0],
            struct.unpack_from("<i", vf3, VOFF + k * 4)[0])
CL = load_charlist(V10 + "/patch.vpp_pc")
def idx(ch):
    cp = ord(ch); return CL.index(cp) if cp in CL else None

def cell(atlas, k, sz=31):
    x, y = uv(k); out = []
    for yy in range(sz):
        row = []
        for xx in range(sz):
            X, Y = x + xx, y + yy
            if X < 0 or Y < 0 or X >= 2048 or Y >= 2048:
                row.append(0); continue
            row.append(dec_block(atlas, ((Y // 4) * BW + X // 4) * 16)[Y % 4][X % 4][3])
        out.append(row)
    return out

def norm(mask_src, w, h, dst=20):
    """mask_src: h x w 的 0/1。裁到 bbox 再缩放到 dst x dst（最近邻）。"""
    xs = [x for y in range(h) for x in range(w) if mask_src[y][x]]
    ys = [y for y in range(h) for x in range(w) if mask_src[y][x]]
    if not xs: return None
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    bw, bh = x1 - x0 + 1, y1 - y0 + 1
    out = [[0] * dst for _ in range(dst)]
    for yy in range(dst):
        sy = y0 + min(bh - 1, yy * bh // dst)
        for xx in range(dst):
            sx = x0 + min(bw - 1, xx * bw // dst)
            out[yy][xx] = mask_src[sy][sx]
    return out

def render(ch, font):
    img = Image.new("L", (64, 64), 0)
    d = ImageDraw.Draw(img)
    d.text((8, 4), ch, fill=255, font=font)
    px = img.load()
    m = [[1 if px[x, y] > 110 else 0 for x in range(64)] for y in range(64)]
    return norm(m, 64, 64)

def iou(a, b):
    if a is None or b is None: return 0.0
    inter = sum(1 for y in range(20) for x in range(20) if a[y][x] and b[y][x])
    uni = sum(1 for y in range(20) for x in range(20) if a[y][x] or b[y][x])
    return inter / uni if uni else 0.0

FONTS = []
for fp in (r"C:/Windows/Fonts/msyh.ttc", r"C:/Windows/Fonts/simsun.ttc",
           r"C:/Windows/Fonts/simhei.ttf", r"C:/Windows/Fonts/msyhbd.ttc"):
    if os.path.exists(fp):
        for sz in (30, 32, 34):
            try: FONTS.append((fp, sz, ImageFont.truetype(fp, sz)))
            except Exception: pass
print("fonts:", [(os.path.basename(f[0]), f[1]) for f in FONTS])

TEST = "你的弟兄们需要保护谈生意"
atlas_data = {n: load_atlas(p, e) for n, (p, e) in ATLASES.items()}
for name, atlas in atlas_data.items():
    print("\n==== %s (md5=%s) ====" % (name, __import__("hashlib").md5(atlas).hexdigest()[:12]))
    offs = []
    for ch in TEST:
        k = idx(ch)
        if k is None: print("  %s 不在 charlist" % ch); continue
        best = (-1, 0.0, None)  # (score, offset, font)
        for fp, sz, font in FONTS:
            tpl = render(ch, font)
            for j in range(max(0, k - 8), min(N, k + 9)):
                s = iou(tpl, norm(cell(atlas, j), 31, 31))
                if s > best[0]: best = (s, j - k, os.path.basename(fp) + ":" + str(sz))
        offs.append(best[1])
        print("  %s idx=%-4d best_off=%+d iou=%.2f (%s)" % (ch, k, best[1], best[0], best[2]))
    if offs:
        from collections import Counter
        print("  --> 偏移分布:", Counter(offs).most_common())
