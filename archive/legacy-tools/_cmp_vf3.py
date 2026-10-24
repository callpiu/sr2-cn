# -*- coding: utf-8 -*-
"""渲染 vf3 指定索引的字形，与 charlist_CH 的对应字比对。
定案「vf3 索引 == charlist 索引 ?」
"""
import sys, os, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp, dxt3_decode
from PIL import Image
import numpy as np

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(os.path.join(G, 'patch.vpp_pc'))
cn = [int(l) for l in v.read(v.find('charlist_CH', 'txt')).decode('utf-8').split('\n') if l.strip().isdigit()]
vb = v.read(v.find('fnt_chinese', 'vf3_pc'))
N = struct.unpack('<I', vb[8:12])[0]
urec = 0xD0 + N * 16
U = struct.unpack('<%di' % N, vb[urec:urec + N * 4])
Vb = urec + N * 4
V = struct.unpack('<%di' % (N - 5), vb[Vb:Vb + (N - 5) * 4])
pe = v.read(v.find('fnt_chinese', 'g_peg_pc'))
rgb, alpha = dxt3_decode(pe, 2048, 2048)
rgb = np.asarray(rgb)
alpha = np.asarray(alpha)
H, W = rgb.shape[0], rgb.shape[1]
print('atlas', W, H, 'N', N)

# U(x) / V(y) grid step 31/32? U 线性 +31 起点156；V 值 1..
def cell_of(k):
    x = U[k]
    y = V[k] if k < len(V) else V[-1]
    return x, y, x + 30, y + 30  # 31px cell

def render_glyphs(idx_list, path, cell=31):
    imgs = []
    for k in idx_list:
        x = U[k]
        y = V[k] if k < len(V) else 0
        a = alpha[y:y + cell, x:x + cell]
        r = 255 - a  # 白底黑字
        imgs.append(Image.fromarray(r.astype('uint8'), 'L').resize((48, 48), Image.NEAREST))
    Wt = 48 * len(imgs)
    canvas = Image.new('L', (Wt, 48), 255)
    for i, im in enumerate(imgs):
        canvas.paste(im, (i * 48, 0))
    canvas.save(path)
    print('saved', path, 'for idx', idx_list)
    return [chr(cn[k]) if 0 <= k < len(cn) and cn[k] >= 32 else '?' for k in idx_list]

# 目标：检查 vf3[k] 是否画出 cn[k]
probe = [371, 1836, 422, 1035, 332, 2415, 496, 324]
labels = render_glyphs(probe, 'F:/sr2-cn/_cmp_vf3_vs_charlist.png')
print('charlist 字:', labels)

# 也检查 vf3[k] 画出的是不是 cn[k-0x20]
probe2 = [k - 0x20 for k in [403, 1868, 454, 1067, 364, 2447, 528, 356]]
labels2 = render_glyphs(probe2, 'F:/sr2-cn/_cmp_vf3_minus32.png')
print('k-32 索引对应 charlist 字:', [chr(cn[k]) if 0<=k<len(cn) and cn[k]>=32 else '?' for k in probe2])
