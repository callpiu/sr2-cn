# -*- coding: utf-8 -*-
"""关键对比：原厂 vf3(2838) vs 补丁 vf3(2795)，同索引渲染。
目标字: 你 的 兄 弟 们
"""
import sys, os, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp, dxt3_decode
from PIL import Image
import numpy as np

def load(vpp_path, tag):
    v = Vpp(vpp_path)
    b = v.read(v.find('charlist_CH', 'txt'))
    cn = [int(l) for l in b.decode('utf-8', 'replace').split('\n') if l.strip().isdigit()]
    vb = v.read(v.find('fnt_chinese', 'vf3_pc'))
    N = struct.unpack('<I', vb[8:12])[0]
    urec = 0xD0 + N * 16
    U = struct.unpack('<%di' % N, vb[urec:urec + N * 4])
    Vb = urec + N * 4
    V = struct.unpack('<%di' % (N - 5), vb[Vb:Vb + (N - 5) * 4])
    pe = v.read(v.find('fnt_chinese', 'g_peg_pc'))
    rgb, alpha = dxt3_decode(pe, 2048, 2048)
    alpha = np.asarray(alpha)
    print('[%s] charlist=%d  vf3 N=%d  U[0:4]=%s' % (tag, len(cn), N, U[:4]))
    return cn, U, V, alpha

def render(alpha, U, V, indices, cell, path):
    imgs = []
    for k in indices:
        x = U[k]; y = V[k] if k < len(V) else 0
        a = alpha[y:y+cell, x:x+cell]
        r = 255 - a
        imgs.append(Image.fromarray(r.astype('uint8'), 'L').resize((48, 48), Image.NEAREST))
    canvas = Image.new('L', (48*len(imgs), 48), 255)
    for i, im in enumerate(imgs):
        canvas.paste(im, (i*48, 0))
    canvas.save(path)
    print('saved', path)

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
cnP, UP, VP, aP = load(os.path.join(G, 'patch.vpp_pc'), 'PATCH-live')
cnO, UO, VO, aO = load('F:/sr2-cn/pristine/patch.vpp_pc', 'PRISTINE')

# 官方 charlist 中目标字的索引
def find(cn, ch):
    cp = ord(ch)
    return cn.index(cp) if cp in cn else None

print('\n== 原厂(2838) charlist 中目标字索引 ==')
for ch in '你的兄弟们赶到他们的目的地':
    i = find(cnO, ch)
    print('  %s -> idx %s' % (ch, i))
print('\n== 补丁(2795) charlist 中目标字索引 ==')
for ch in '你的兄弟们赶到他们的目的地':
    i = find(cnP, ch)
    print('  %s -> idx %s' % (ch, i))

# 渲染：原厂 vf3 在『原厂索引』处
idxO = [find(cnO, ch) for ch in '你的兄弟们赶到他们的目的地']
render(aO, UO, VO, [i for i in idxO if i is not None], 20, 'F:/sr2-cn/_cmp_pristine_vf3_at_official_idx.png')

# 渲染：原厂 vf3 在『补丁索引』处
idxP = [find(cnP, ch) for ch in '你的兄弟们赶到他们的目的地']
render(aO, UO, VO, [i for i in idxP if i is not None and i < len(UO)], 20, 'F:/sr2-cn/_cmp_pristine_vf3_at_patch_idx.png')

# 渲染：补丁 vf3 在『补丁索引』处
render(aP, UP, VP, [i for i in idxP if i is not None and i < len(UP)], 31, 'F:/sr2-cn/_cmp_patch_vf3_at_patch_idx.png')

# 渲染：补丁 vf3 在『原厂索引』处
render(aP, UP, VP, [i for i in idxO if i is not None and i < len(UP)], 31, 'F:/sr2-cn/_cmp_patch_vf3_at_official_idx.png')
