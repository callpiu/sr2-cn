# -*- coding: utf-8 -*-
"""决定性诊断：活动字幕 slot 在 (哪张表/哪个偏移/哪张图集) 下渲染成什么字形。
目标记录 slot(内存) = [403,1868,454,1067,364,2447,528,356,364,1868,1885,1868,781,261]
期望正确 = 你的兄弟们赶到他们的目的地。
"""
import os, sys, struct, re
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:/sr2-cn")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"


# ---- 用 minivpp 读 vpp ----
import minivpp


def load_table(vpp):
    v = minivpp.MiniVpp(vpp)
    e = v.find("charlist_CH", "txt")
    raw = v.read(e)
    out = []
    for ln in raw.split(b"\n"):
        ln = ln.strip()
        if not ln or ln.startswith(b"//"):
            continue
        try:
            out.append(int(ln))
        except Exception:
            pass
    return out


def load_vf3(vpp):
    v = minivpp.MiniVpp(vpp)
    e = v.find("fnt_chinese", "vf3_pc")
    vf3 = bytes(v.read(e))
    N = struct.unpack_from("<i", vf3, 0x08)[0]
    U0 = 0xD0 + N * 16
    U = list(struct.unpack_from("<%di" % N, vf3, U0))
    nV = (len(vf3) - (U0 + N * 4)) // 4
    V = list(struct.unpack_from("<%di" % nV, vf3, U0 + N * 4)) + [0] * (N - nV)
    return N, U, V


def load_atlas(vpp):
    from sr2lib import dxt3_decode
    v = minivpp.MiniVpp(vpp)
    e = v.find("fnt_chinese", "g_peg_pc")
    return dxt3_decode(bytes(v.read(e)), 2048, 2048)[1]


print("loading...")
patch_tbl = load_table("_v534_build.vpp_pc")
off_tbl = load_table("pristine/patch.vpp_pc")
Np, Up, Vp_ = load_vf3("_v534_build.vpp_pc")
Nc, Uc, Vc = load_vf3("pristine/patch.vpp_pc")
atlas = load_atlas("_v534_build.vpp_pc")
print("patch tbl=%d off tbl=%d patchvf3=%d offvf3=%d atlas=%s" % (len(patch_tbl), len(off_tbl), Np, Nc, atlas.shape))

MEM_SLOTS = [403, 1868, 454, 1067, 364, 2447, 528, 356, 364, 1868, 1885, 1868, 781, 261]


def tile(U, V, i, h=30, w=31):
    if not (0 <= i < len(U)):
        return np.zeros((h, w), np.uint8)
    x, y = U[i], V[i]
    g = atlas[y:y + h, x:x + w]
    if g.shape != (h, w):
        pad = np.zeros((h, w), np.uint8)
        pad[:g.shape[0], :g.shape[1]] = g
        g = pad
    return g


def render_slots(U, V, title, fname, off, n=len(MEM_SLOTS)):
    tiles = []
    for k in range(n):
        s = MEM_SLOTS[k]
        i = s - off
        tiles.append(tile(U, V, i))
        tiles.append(np.full((30, 2), 255, np.uint8))
    s = np.concatenate(tiles, axis=1)
    Image.fromarray(255 - s).resize((s.shape[1] * 5, s.shape[0] * 5), Image.NEAREST).save(fname)
    print("%-46s (off=%d) -> %s" % (title, off, fname))


# 索引必须能超过 2795，否则 vf3 越界
render_slots(Up, Vp_, "patch-vf3, slot-0x20", r"F:\sr2-cn\_diag_patch_off32.png", 0x20)
render_slots(Up, Vp_, "patch-vf3, slot(no off)", r"F:\sr2-cn\_diag_patch_off0.png", 0)
render_slots(Uc, Vc, "pristine-vf3, slot-0x20", r"F:\sr2-cn\_diag_pris_off32.png", 0x20)
render_slots(Uc, Vc, "pristine-vf3, slot(no off)", r"F:\sr2-cn\_diag_pris_off0.png", 0)
