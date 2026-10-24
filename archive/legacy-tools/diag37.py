# -*- coding: utf-8 -*-
# diag37: 像素级验证——atlas B 在 idx g 处的 cell 是否画着"乱码字"
import sys, struct
sys.path.insert(0, 'F:/sr2-cn')
import numpy as np
import sr2lib

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
vp = sr2lib.Vpp(GAME + r'\patch.vpp_pc')
tx = sr2lib.Vpp(GAME + r'\textures.vpp_pc')

CPS = [int(l) for l in vp.read(vp.find('charlist_CH', 'txt'))
       .decode('utf-8').split('\n') if l.strip().isdigit()]
N = len(CPS)
CHR = ''.join(chr(c) for c in CPS)

vf3 = bytes(vp.read(vp.find('fnt_chinese', 'vf3_pc')))
U = list(struct.unpack_from(f'<{N}i', vf3, 0xAF6C))
V = list(struct.unpack_from(f'<{N}i', vf3, 0xDB18))

# atlas A (patch g_peg) and atlas B (textures fnt_chinese.)
_, aA = sr2lib.dxt3_decode(bytes(vp.read(vp.find('fnt_chinese', 'g_peg_pc'))), 2048, 2048)
entB = tx.find('fnt_chinese', '')
_, aB = sr2lib.dxt3_decode(bytes(tx.read(entB)), 2048, 2048)
print('atlas A', aA.shape, 'atlas B', aB.shape)

CELL = 31
def cell(img, g):
    x, y = U[g], V[g]
    return img[y:y+28, x:x+CELL].astype(np.float32)

def ncc(a, b):
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a*a).sum() * (b*b).sum())
    return float((a*b).sum() / d) if d > 0 else 0.0

# constraints: glyph idx g shows screen char (rank r) instead of true char (=g)
CONS = [(371, '任'), (1836, '璨'), (2452, '偶'), (2093, '巧'), (268, '位'),
        (2667, '雄'), (2296, '衡'), (391, '伪'), (1190, '该')]
# extra from REC2 (要 anomaly checked separately)
CONS2 = [(2328, '要校')]  # placeholder

print('\ng | true-char(B@g vs A@g) | screen-char(B@g vs A@r) | verdict')
for g, sc in CONS:
    r = CHR.index(sc)
    cB = cell(aB, g)
    sA_true = ncc(cB, cell(aA, g))
    sA_scr  = ncc(cB, cell(aA, r))
    verdict = 'SCREEN-CHAR!' if sA_scr > sA_true else 'true-char'
    print(f'{g:5d} | {CHR[g]} true={sA_true:.3f} | {sc} r={r} scr={sA_scr:.3f} | {verdict}')

# also control: A@g vs A@g should be 1.0 trivially; check A/B same-index similarity distribution
print('\ncontrol: similarity of B@g vs A@g for 20 random g:')
import random
random.seed(1)
for g in random.sample(range(50, 2700), 20):
    print(f'  g={g} {CHR[g]} ncc={ncc(cell(aB,g), cell(aA,g)):.3f}')
