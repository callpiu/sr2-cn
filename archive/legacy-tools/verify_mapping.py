# -*- coding: utf-8 -*-
"""决定性验证: 9个乱码字 在各种 (表, UV) 组合下的图集字形。

核心问题: 活动字幕磁盘 slot = 某表索引 + 0x20。
运行时用 (哪张 charlist) x (哪张 vf3 UV) 把它渲染成字形?
"""
import os, sys, struct, re
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
PRISTINE = r"F:\sr2-cn\pristine\patch.vpp_pc"


def load_table_src(path_or_name):
    """path_or_name: 绝对路径 或 G 下文件名"""
    p = path_or_name if os.path.isabs(path_or_name) else os.path.join(G, path_or_name)
    v = Vpp(p)
    e = v.find("charlist_CH", "txt")
    buf = v.read(e)
    end = buf.find(b'//ENDOFFILE')
    if end < 0:
        end = len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]


def load_vf3(path_or_name):
    p = path_or_name if os.path.isabs(path_or_name) else os.path.join(G, path_or_name)
    v = Vpp(p)
    vf3 = bytes(v.read(v.find("fnt_chinese", "vf3_pc")))
    N = struct.unpack_from("<i", vf3, 0x08)[0]
    U0 = 0xD0 + N * 16
    U = list(struct.unpack_from("<%di" % N, vf3, U0))
    nV = (len(vf3) - (U0 + N * 4)) // 4
    V = list(struct.unpack_from("<%di" % nV, vf3, U0 + N * 4)) + [0] * (N - nV)
    return N, U, V


# 图集: patch 的 g_peg_pc
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
_, atlas = dxt3_decode(bytes(vp.read(vp.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)

patch_tbl = load_table_src("patch.vpp_pc")
off_tbl = load_table_src(PRISTINE)
Np, Up, Vp_ = load_vf3("patch.vpp_pc")
Nc, Uc, Vc = load_vf3("common.vpp_pc")
print("patch 表=%d  vf3=%d" % (len(patch_tbl), Np))
print("原厂 表=%d" % len(off_tbl))
print("common vf3=%d" % Nc)


def tile(U, V, i, h=30, w=31):
    x, y = U[i], V[i]
    g = atlas[y:y + h, x:x + w]
    if g.shape != (h, w):
        pad = np.zeros((h, w), np.uint8)
        pad[:g.shape[0], :g.shape[1]] = g
        g = pad
    return g


targets = ["你", "的", "弟", "兄", "们", "需", "要", "保", "护"]
disp    = ["任", "璨", "偶", "巧", "位", "雄", "衡", "伪", "该"]


def render_row(tbl, U, V, title, fname):
    tiles, labels = [], []
    for k, ch in enumerate(targets):
        ci = tbl.index(ord(ch)) if ord(ch) in tbl else -1
        if ci >= 0 and ci < len(U):
            tiles.append(tile(U, V, ci))
        else:
            tiles.append(np.zeros((30, 31), np.uint8))
        tiles.append(np.full((30, 2), 255, np.uint8))
        labels.append("%s@%d" % (ch, ci))
        di = tbl.index(ord(disp[k])) if ord(disp[k]) in tbl else -1
        if di >= 0 and di < len(U):
            tiles.append(tile(U, V, di))
        else:
            tiles.append(np.zeros((30, 31), np.uint8))
        tiles.append(np.full((30, 4), 120, np.uint8))
        labels.append("%s@%d" % (disp[k], di))
    s = np.concatenate(tiles, axis=1)
    Image.fromarray(255 - s).resize((s.shape[1] * 6, s.shape[0] * 6), Image.NEAREST).save(fname)
    print("%-40s %s" % (title, " ".join(labels)))
    print("   -> %s" % fname)


print()
print("图序: [正确字@idx | 乱码字@idx] x9")
render_row(patch_tbl, Up, Vp_, "patch表 x patch-vf3 UV", r"F:\sr2-cn\_verify_A_patchUV.png")
render_row(off_tbl, Up, Vp_, "原厂表 x patch-vf3 UV", r"F:\sr2-cn\_verify_B_offUV.png")
render_row(patch_tbl, Uc, Vc, "patch表 x common-vf3 UV", r"F:\sr2-cn\_verify_C_commonUV.png")
render_row(off_tbl, Uc, Vc, "原厂表 x common-vf3 UV", r"F:\sr2-cn\_verify_D_off_commonUV.png")
