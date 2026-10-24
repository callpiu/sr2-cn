# -*- coding: utf-8 -*-
"""验证 official 2838 字表 与 common.vpp 的 2838 vf3 是否索引对齐，
然后用 REC2 的 glyph 值走 2838 vf3，看是否得到观测乱码。
"""
import sys, os, struct, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp, dxt3_decode
from PIL import Image
import numpy as np

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'


def load_cl(vp, name):
    buf = vp.read(vp.find(name, 'txt'))
    end = buf.find(b'//ENDOFFILE')
    if end < 0:
        end = len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]


def load_vf3(vp, name):
    vb = vp.read(vp.find(name, 'vf3_pc'))
    N = struct.unpack('<I', vb[8:12])[0]
    urec = 0xD0 + N * 16
    U = struct.unpack('<%di' % N, vb[urec:urec + N * 4])
    Vb = urec + N * 4
    V = struct.unpack('<%di' % (N - 5), vb[Vb:Vb + (N - 5) * 4])
    return N, U, V


pv = Vpp('F:/sr2-cn/pristine/patch.vpp_pc')
clO = load_cl(pv, 'charlist_CH')
Nc, Uc, Vc = load_vf3(pv, 'fnt_chinese')
print('pristine(patch.vpp): charlist=%d vf3N=%d' % (len(clO), Nc))

# common.vpp 的 vf3 (2838) —— 无对应 charlist，但应与 official 表配对
cv = Vpp(os.path.join(G, 'common.vpp_pc'))
Ncm, Ucm, Vcm = load_vf3(cv, 'fnt_chinese')
print('common.vpp vf3N=%d' % Ncm)

# atlas: patch.vpp 的 g_peg_pc; common.vpp 可能没有 peg（在 textures.vpp）
def load_atlas(vp):
    pe = vp.read(vp.find('fnt_chinese', 'g_peg_pc'))
    _, a = dxt3_decode(pe, 2048, 2048)
    return np.asarray(a)
aP = load_atlas(pv)
aC = aP  # common.vpp 无 peg，atlas 在 textures.vpp（原厂）。此处先复用 pristine 的 atlas 观察字形
print('atlas shape', aP.shape)


def render(alpha, U, V, idx_list, cell, path, gap=31):
    imgs = []
    for k in idx_list:
        if k >= len(U) or k < 0:
            imgs.append(Image.new('L', (40, 40), 120)); continue
        x = U[k]; y = V[k] if k < len(V) else 0
        a = alpha[y:y + cell, x:x + cell]
        imgs.append(Image.fromarray((255 - a).astype('uint8'), 'L').resize((44, 44), Image.NEAREST))
    canvas = Image.new('L', (44 * len(imgs), 44), 255)
    for i, im in enumerate(imgs):
        canvas.paste(im, (i * 44, 0))
    canvas.save(path)
    print('saved', path)


def idx_of(cl, ch):
    cp = ord(ch)
    return cl.index(cp) if cp in cl else None


# 用 patch(2795) 的 charlist idx 渲染 common(2838) vf3
clP = load_cl(Vpp(os.path.join(G, 'patch.vpp_pc')), 'charlist_CH')
probe2 = [idx_of(clP, c) for c in '你的兄弟们赶到']
render(aC, Ucm, Vcm, [k for k in probe2 if k is not None], 31, 'F:/sr2-cn/_E2_commonvf3_atPidx.png')
print('patch idx:', probe2)

# ★ 最关键：直接用 REC2 的 glyph 值（slot）渲染 common(2838) vf3
rec2_slots = [403, 1868, 1067, 454, 364, 2328, 510, 613, 2389, 502, 1995, 1824, 1159, 2822, 423, 1222, 356, 364, 460, 2563, 2312, 511]
render(aC, Ucm, Vcm, [s for s in rec2_slots if s < Ncm], 31, 'F:/sr2-cn/_E3_commonvf3_slotdirect.png')
print('REC2 true: 你的弟兄们要出去谈几笔生意，保护他们免遭袭击')

# 同时用 patch(2795) vf3 渲染同样 slot，作对照
Np, Up, Vp = load_vf3(Vpp(os.path.join(G, 'patch.vpp_pc')), 'fnt_chinese')
render(aP, Up, Vp, [s for s in rec2_slots if s < Np], 31, 'F:/sr2-cn/_E4_patchvf3_slotdirect.png')
