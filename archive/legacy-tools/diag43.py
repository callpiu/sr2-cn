# -*- coding: utf-8 -*-
# diag43: ASCII-art 用 RGB 亮度渲染 B cell（负像修正），并排比对
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
cb0 = len(vf3c) - 8 * Nc
cU = struct.unpack_from(f'<{Nc}i', vf3c, cb0)
cV = struct.unpack_from(f'<{Nc}i', vf3c, cb0 + 4 * Nc)

rgbA, alA = sr2lib.dxt3_decode(bytes(vp.read(vp.find('fnt_chinese', 'g_peg_pc'))), 2048, 2048)
rgbB, alB = sr2lib.dxt3_decode(bytes(tx.read(tx.find('fnt_chinese', ''))), 2048, 2048)

def art(img, x, y, w, h, thresh=110, invert=False):
    g = img[y:y+h, x:x+w].astype(np.float32)
    if g.ndim == 3:
        g = g.mean(axis=2)
    lines = []
    for r in range(0, h - 1, 2):
        line = ''
        for c in range(w):
            v = max(g[r, c], g[r + 1, c])
            if invert:
                v = 255 - v
            line += '#' if v > thresh else '.'
        lines.append(line)
    return lines

def show(tag, lines):
    print(f'--- {tag} ---')
    print('\n'.join(lines))

# B: try rgb direct (glyph dark on light?) and inverted
PAIRS = [(371, '任'), (1836, '璨'), (391, '伪'), (1190, '该')]
for g, sc in PAIRS:
    r = CHR.index(sc)
    bx, by = cU[g], cV[g]
    print(f'\n######## glyph {g}: B cell vs A[{g}]({CHR[g]}) vs A[{r}]({sc}) ########')
    show(f'B_rgb@({bx},{by})', art(rgbB, bx, by, 20, 36))
    show(f'B_rgb_inv', art(rgbB, bx, by, 20, 36, invert=True))
    show(f'A[{g}]={CHR[g]}', art(alA, pU[g], pV[g], 31, 28))
    show(f'A[{r}]={CHR[r]}', art(alA, pU[r], pV[r], 31, 28))
