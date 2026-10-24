# -*- coding: utf-8 -*-
# diag39: 像素验证——图集B(18px) 在 idx g 处是否画着"乱码字"(=A@r)
import sys, struct
sys.path.insert(0, 'F:/sr2-cn')
import numpy as np
from PIL import Image
import sr2lib

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
vp = sr2lib.Vpp(GAME + r'\patch.vpp_pc')
tx = sr2lib.Vpp(GAME + r'\textures.vpp_pc')

CPS = [int(l) for l in vp.read(vp.find('charlist_CH', 'txt'))
       .decode('utf-8').split('\n') if l.strip().isdigit()]
N = len(CPS)
CHR = ''.join(chr(c) for c in CPS)

vf3p = bytes(vp.read(vp.find('fnt_chinese', 'vf3_pc')))
pU = struct.unpack_from(f'<{N}i', vf3p, 0xAF6C)
pV = struct.unpack_from(f'<{N}i', vf3p, 0xDB18)

vf3c = bytes(tx and __import__('sr2lib').Vpp(GAME + r'\common.vpp_pc').read(
    __import__('sr2lib').Vpp(GAME + r'\common.vpp_pc').find('fnt_chinese', 'vf3_pc')))
Nc = 2838
base = len(vf3c) - 8 * Nc
cU = struct.unpack_from(f'<{Nc}i', vf3c, base)
cV = struct.unpack_from(f'<{Nc}i', vf3c, base + 4 * Nc)
print('common cell pitch check:', cU[:8], 'V', cV[:8])
print('common x range', min(cU), max(cU), 'y range', min(cV), max(cV))
print('patch  x range', min(pU), max(pU), 'y range', min(pV), max(pV))

_, aA = sr2lib.dxt3_decode(bytes(vp.read(vp.find('fnt_chinese', 'g_peg_pc'))), 2048, 2048)
_, aB = sr2lib.dxt3_decode(bytes(tx.read(tx.find('fnt_chinese', ''))), 2048, 2048)

# measure actual cell size of B: find pitch differences -> 18. assume glyph box ~18x18
def cellA(g, w=31, h=28):
    x, y = pU[g], pV[g]
    return Image.fromarray(aA[y:y+h, x:x+w])

def cellB(g, w=18, h=18):
    x, y = cU[g], cV[g]
    return Image.fromarray(aB[y:y+h, x:x+w])

def ncc(a_img, b_img):
    a = np.asarray(a_img, np.float32)
    b = np.asarray(b_img, np.float32)
    if b.shape != a.shape:
        b = np.asarray(b_img.resize((a.shape[1], a.shape[0]), Image.BILINEAR), np.float32)
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a*a).sum()*(b*b).sum())
    return float((a*b).sum()/d) if d > 0 else 0.0

# valid pairs (unaffected by probe): g(new idx) -> screen char
PAIRS = [(371, '任'), (1836, '璨'), (2667, '雄'), (2296, '衡'), (391, '伪'), (1190, '该')]
print('\ng | char@A[g] | sim(B@g, A@g) | screen | r | sim(B@g, A@r) | verdict')
for g, sc in PAIRS:
    r = CHR.index(sc)
    b = cellB(g)
    s_true = ncc(b, cellA(g))
    s_scr = ncc(b, cellA(r))
    v = 'SCREEN!' if s_scr > s_true else 'true'
    print(f'{g:5d} | {CHR[g]} | {s_true:+.3f} | {sc} | {r} | {s_scr:+.3f} | {v}')

# sanity: does B look like a proper glyph grid at all? render a strip of B cells as text-art check
# save a comparison sheet for eyeball fallback
sheet = Image.new('L', (8 * 62, 3 * 56), 0)
for k, (g, sc) in enumerate(PAIRS[:6]):
    r = CHR.index(sc)
    sheet.paste(cellB(g).resize((31, 31)), (k * 62, 0))
    sheet.paste(cellA(g).resize((31, 31)), (k * 62, 34))
    sheet.paste(cellA(r).resize((31, 31)), (k * 62, 68)) if False else None
sheet.save(r'F:/sr2-cn/_diag39_sheet.png')
print('sheet saved (row1 = B@g, row2 = A@g)')
