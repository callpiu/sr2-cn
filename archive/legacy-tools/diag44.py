# -*- coding: utf-8 -*-
# diag44: 全量 NCC 矩阵匹配 A(2795) x B(2838)，验证乱码映射并求完整新旧字序
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

rgbA, alA = sr2lib.dxt3_decode(bytes(vp.read(vp.find('fnt_chinese', 'g_peg_pc'))), 2048, 2048)
rgbB, alB = sr2lib.dxt3_decode(bytes(tx.read(tx.find('fnt_chinese', ''))), 2048, 2048)

W, H = 20, 28   # normalized cell
CW = 18         # B crop width (variable-width font, CJK ~18)

def norm(x):
    x = x.astype(np.float32).flatten()
    x = x - x.mean()
    n = np.linalg.norm(x)
    return x / n if n > 0 else x

# A cells from alpha (glyph shape)
Amat = np.zeros((N, W * H), np.float32)
for g in range(N):
    cell = alA[pV[g]:pV[g] + H, pU[g]:pU[g] + 31].astype(np.float32)
    im = np.asarray(Image_fromarray(cell), np.float32) if False else cell
    # resize 31xH -> WxH via simple stride (nearest)
    idx = (np.arange(W) * 31 // W)
    small = cell[:, idx]
    Amat[g] = norm(small)

# B cells: try alpha channel first
def build_B(chan):
    M = np.zeros((Nc, W * H), np.float32)
    for k in range(Nc):
        cell = chan[cV[k]:cV[k] + H, cU[k]:cU[k] + CW].astype(np.float32)
        if cell.shape != (H, CW):
            pad = np.zeros((H, CW), np.float32)
            pad[:cell.shape[0], :cell.shape[1]] = cell
            cell = pad
        idx = (np.arange(W) * CW // W)
        small = cell[:, idx]
        M[k] = norm(small)
    return M

def Image_fromarray(a):
    from PIL import Image
    return Image.fromarray(a)

Bmat_alpha = build_B(alB)
S = Bmat_alpha @ Amat.T           # [Nc, N] cosine similarity
bestA = S.argmax(axis=1)
bestS = S.max(axis=1)

PAIRS = [(371, 336, '任'), (1836, 1784, '璨'), (1035, 410, '偶'), (422, 967, '巧'),
         (332, 362, '位'), (2667, 2656, '雄'), (2296, 2268, '衡'), (2296, 1458, '校'),
         (391, 301, '亡'), (1190, 362, '位'), (324, 2514, '通'), (428, 543, '匪'),
         (2531, 458, '冰'), (2280, 1243, '挺'), (479, 1221, '拮'), (478, 2268, '衡'),
         (581, 535, '勾'), (2357, 2491, '远'), (470, 2234, '藐'), (1963, 287, '乱'),
         (1792, 1292, '携'), (1127, 354, '伪'), (2790, 2342, '该')]
hit = 0
print('g -> predicted(A-nearest) | expected | ok?  (top1 sim, margin)')
for g, r, name in PAIRS:
    p = bestA[g]
    order = np.argsort(S[g])[::-1][:3]
    ok = (p == r)
    hit += ok
    print(f'{g:5d} -> {CHR[p]} ({p}) | {name} ({r}) | {"OK" if ok else "MISS"}  '
          f'top: {[(CHR[i], round(float(S[g][i]),3)) for i in order]}')
print(f'\nhits: {hit}/{len(PAIRS)}')
np.save(r'F:/sr2-cn/_match_B2A.npy', bestA)
np.save(r'F:/sr2-cn/_match_S.npy', S.astype(np.float16))
print('match quality: mean top1', float(bestS.mean()), ' min', float(bestS.min()),
      ' <0.5 count', int((bestS < 0.5).sum()))
