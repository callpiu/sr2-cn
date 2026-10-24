# -*- coding: utf-8 -*-
# diag48: 改进版像素匹配（LANCZOS+模糊），验证 18px 字体真实字序
import sys, struct
sys.path.insert(0, 'F:/sr2-cn')
import numpy as np
from PIL import Image, ImageFilter
import sr2lib

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
vp = sr2lib.Vpp(GAME + r'\patch.vpp_pc')
tx = sr2lib.Vpp(GAME + r'\textures.vpp_pc')
cm = sr2lib.Vpp(GAME + r'\common.vpp_pc')

CPS = [int(l) for l in vp.read(vp.find('charlist_CH', 'txt'))
       .decode('utf-8').split('\n') if l.strip().isdigit()]
N = len(CPS)
CHR = ''.join(chr(c) for c in CPS)

vf3p = bytes(vp.read(vp.find('fnt_chinese', 'vf3_pc')))
pU = struct.unpack_from(f'<{N}i', vf3p, 0xAF6C)
pV = struct.unpack_from(f'<{N}i', vf3p, 0xDB18)
vf3c = bytes(cm.read(cm.find('fnt_chinese', 'vf3_pc')))
Nc = 2838
cb = len(vf3c) - 8 * Nc
cU = list(struct.unpack_from(f'<{Nc}i', vf3c, cb))
cV = list(struct.unpack_from(f'<{Nc}i', vf3c, cb + 4 * Nc))

rgbA, alA = sr2lib.dxt3_decode(bytes(vp.read(vp.find('fnt_chinese', 'g_peg_pc'))), 2048, 2048)
rgbB, alB = sr2lib.dxt3_decode(bytes(tx.read(tx.find('fnt_chinese', ''))), 2048, 2048)
grayB = rgbB.mean(axis=2)

SZ = 16

def feat(img_pil):
    im = img_pil.resize((SZ, SZ), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1))
    a = np.asarray(im, np.float32)
    a -= a.mean()
    n = np.linalg.norm(a)
    return (a / n).flatten() if n > 0 else a.flatten()

def to_pil(arr):
    a = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(a)

# A features (alpha shape)
Af = np.zeros((N, SZ * SZ), np.float32)
for g in range(N):
    Af[g] = feat(to_pil(alA[pV[g]:pV[g] + 28, pU[g]:pU[g] + 31]))

# B cell widths (variable): next x on same row, else 18
ROW = 31
xs_by_row = {}
for k in range(Nc):
    xs_by_row.setdefault(cV[k], []).append((cU[k], k))
for r in xs_by_row:
    xs_by_row[r].sort()

def b_width(k):
    x, y = cU[k], cV[k]
    lst = xs_by_row[y]
    i = [t[1] for t in lst].index(k)
    if i + 1 < len(lst):
        return min(18, max(6, lst[i + 1][0] - x - 1))
    return 18

# B features: try rgb and (255-grayB) and alpha
for cname, chan in (('grayB', grayB), ('grayB_inv', 255 - grayB),
                    ('alB', alB.astype(np.float32)), ('alB_inv', 255 - alB.astype(np.float32))):
    Bf = np.zeros((Nc, SZ * SZ), np.float32)
    for k in range(Nc):
        w = b_width(k)
        cell = chan[cV[k] + 1:cV[k] + 27, cU[k] + 1:cU[k] + 1 + w]
        if cell.size == 0:
            continue
        Bf[k] = feat(to_pil(cell))
    S = Bf @ Af.T
    best = S.argmax(axis=1)
    # validate on REC1 9 pairs
    CONS = {371: 336, 1836: 1784, 1035: 410, 422: 967, 332: 362,
            2667: 2656, 2296: 2268, 391: 354, 1190: 2342}
    hits = sum(1 for g, r in CONS.items() if best[g] == r)
    # control: identity rate on random cells
    random_ok = 0
    import random
    random.seed(3)
    sample = random.sample(range(50, 2700), 30)
    for g in sample:
        if best[g] == g:
            random_ok += 1
    print(f'{cname:10s}: REC1-pairs {hits}/9   identity-control {random_ok}/30')
    if hits >= 5:
        for g, r in CONS.items():
            top = np.argsort(S[g])[::-1][:3]
            print(f'   g={g} expect {CHR[r]} pred {CHR[int(best[g])]} '
                  f'top: {[(CHR[int(t)], round(float(S[g][t]), 3)) for t in top]}')
        np.save(r'F:/sr2-cn/_B_order.npy', best)
