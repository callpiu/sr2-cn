"""v418 字形渲染验证：从构建产物提取 fnt_chinese 图集，按 vf3 的 U/V 显式坐标取出字形单元，
确认 新索引(2224/2256/2261/2293/2552/2584) 的字形 == 目标字的原始字形（像素一致）。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

OUT = r"F:\sr2-cn\_fix_candidates\patch_v418.vpp_pc"
OUTDIR = r"F:\sr2-cn\_fix_candidates\render_check"
os.makedirs(OUTDIR, exist_ok=True)

v = Vpp(OUT)
# 图集
e_at = v.find("fnt_chinese", "g_peg_pc")
at = v.read(e_at)
rgb, alpha = dxt3_decode(at, 2048, 2048)
# vf3
e_vf3 = v.find("fnt_chinese", "vf3_pc")
vo = v.data_start + e_vf3['body']

def glyph_cell(idx, cell=31):
    U = struct.unpack_from('<i', v.data, vo + 0xAF6C + idx*4)[0]
    V = struct.unpack_from('<i', v.data, vo + 0xDB18 + idx*4)[0]
    # 取 cell x cell
    x0, y0 = U, V
    import numpy as np
    a = alpha[y0:y0+cell, x0:x0+cell]
    return U, V, a

def diff(a, b):
    return int((a != b).sum())

# 目标：徒(1058), 录(1045), 弹(1041) 原始；新索引对应
pairs = [
    ('徒-src', 1058, None),
    ('徒-newA', 2224, 1058),   # slot-0x40 路径
    ('徒-newB', 2256, 1058),   # slot-0x20 路径
    ('录-src', 1045, None),
    ('录-newA', 2261, 1045),
    ('录-newB', 2293, 1045),
    ('弹-src', 1041, None),
    ('弹-newA', 2552, 1041),
    ('弹-newB', 2584, 1041),
    ('建-对照', 1026, None),    # 原本徒会错显示的坏字
]

import numpy as np
from PIL import Image
results = []
for name, idx, ref in pairs:
    U, V, a = glyph_cell(idx)
    # 保存 alpha 为 PNG（黑底白字）
    img = Image.fromarray((a * (255//17)).astype('uint8'), 'L')
    img.save(os.path.join(OUTDIR, "%s_idx%d.png" % (name, idx)))
    rec = (U, V, tuple(struct.unpack_from('<IIII', v.data, vo + 0xD0 + idx*16)))
    results.append((name, idx, U, V, rec))
    print("%-10s idx=%-5d U=%-5d V=%-5d rec=%s" % (name, idx, U, V, rec))

print("\n--- 像素一致性（新索引 vs 目标字原始字形）---")
for name, idx, ref in pairs:
    if ref is None:
        continue
    Ua, Va, _ = glyph_cell(idx)
    Ur, Vr, _ = glyph_cell(ref)
    a_new = alpha[Va:Va+31, Ua:Ua+31]
    a_ref = alpha[Vr:Vr+31, Ur:Ur+31]
    d = diff(a_new, a_ref)
    print("  %-10s(idx %d) vs src(idx %d) : 像素差=%d  -> %s" % (
        name, idx, ref, d, "完全一致" if d == 0 else "有差异!!"))

# 徒新 vs 建对照（应明显不同）
Ua, Va, _ = glyph_cell(2224)
Ub, Vb, _ = glyph_cell(1026)
da = diff(alpha[Va:Va+31, Ua:Ua+31], alpha[Vb:Vb+31, Ub:Ub+31])
print("\n  徒-newA(idx2224) vs 建(idx1026) 像素差=%d (应很大，证明不再是建)" % da)
print("  渲染图已存至:", OUTDIR)
