# -*- coding: utf-8 -*-
# diag42: ASCII-art 目视比对——B@g vs A@g(真字) vs A@r(乱码字)
import sys, struct
sys.path.insert(0, 'F:/sr2-cn')
import numpy as np
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
cU = struct.unpack_from(f'<{Nc}i', vf3c, cb)
cV = struct.unpack_from(f'<{Nc}i', vf3c, cb + 4 * Nc)

_, aA = sr2lib.dxt3_decode(bytes(vp.read(vp.find('fnt_chinese', 'g_peg_pc'))), 2048, 2048)
_, aB = sr2lib.dxt3_decode(bytes(tx.read(tx.find('fnt_chinese', ''))), 2048, 2048)

def art(img, x, y, w, h, thresh=100):
    g = img[y:y+h, x:x+w]
    lines = []
    for r in range(0, g.shape[0], 2):  # 2 rows -> 1 char row for aspect
        line = ''
        for c in range(g.shape[1]):
            v = g[r, r+1 if r+1 < g.shape[0] else r].max() if False else max(g[r, c], g[min(r+1, g.shape[0]-1), c])
            line += '#' if v > thresh else '.'
        lines.append(line)
    return lines

PAIRS = [(371, '任'), (1836, '璨'), (391, '亡伪位置占'), (2296, '衡校'), (1190, '该'), (2667, '雄')]
PAIRS = [(371, '任'), (1836, '璨'), (391, '伪'), (2296, '衡校'), (1190, '该'), (2667, '雄')]

for g, screens in PAIRS:
    r_list = [CHR.index(c) for c in screens if c in CHR]
    bx, by = cU[g], cV[g]
    print(f'\n######## glyph {g}  B@({bx},{by}) ########')
    b_art = art(aB, bx, by, 20, 36)
    a_true = art(aA, pU[g], pV[g], 31, 28)
    print('--- atlas B cell (subtitle?) ---')
    print('\n'.join(b_art))
    print(f'--- atlas A @{g} = {CHR[g]} (true) ---')
    print('\n'.join(a_true))
    for r in r_list:
        print(f'--- atlas A @{r} = {CHR[r]} (screen candidate) ---')
        print('\n'.join(art(aA, pU[r], pV[r], 31, 28)))
