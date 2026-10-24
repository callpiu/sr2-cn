# -*- coding: utf-8 -*-
# diag45: B 通道/偏移组合搜索——找出能让 6 个验证对命中的预处理组合
import sys, struct, itertools
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
grayA = rgbA.mean(axis=2)
grayB = rgbB.mean(axis=2)

W, H = 20, 28

def norm_flat(cell):
    x = cell.astype(np.float32).flatten()
    x -= x.mean()
    n = np.linalg.norm(x)
    return x / n if n > 0 else x

def down(cell, srcw):
    idx = (np.arange(W) * srcw // W)
    return cell[:, idx]

# A matrix from alpha shape
Amat = np.zeros((N, W * H), np.float32)
for g in range(N):
    Amat[g] = norm_flat(down(alA[pV[g]:pV[g] + H, pU[g]:pU[g] + 31], 31))

VALID = [(371, 336), (1836, 1784), (2667, 2656), (391, 301), (324, 2514), (470, 2234)]
# note: using REC2-straight alignment pairs (意->伪 354? use 1127->354) - include both variants
VALID += [(1127, 354), (2531, 458), (2280, 1243), (1963, 287), (1792, 1292), (2357, 2491),
          (581, 535), (478, 2268), (428, 543), (479, 1221), (1035, 410), (422, 967)]

chan_variants = {'grayB': grayB, 'grayB_inv': 255 - grayB,
                 'alB': alB.astype(np.float32), 'alB_inv': 255 - alB.astype(np.float32),
                 'grayB_x_alB': grayB * (alB.astype(np.float32) / 255.0)}

best_combo = None
for cname, chan in chan_variants.items():
    for dx in range(0, 4):
        for dy in range(0, 4):
            rows = []
            for g, r in VALID:
                x, y = cU[g] + dx, cV[g] + dy
                cell = chan[y:y + H, x:x + 18]
                if cell.shape != (H, 18):
                    cell = np.zeros((H, 18))
                rows.append(norm_flat(down(cell, 18)))
            M = np.array(rows, np.float32) @ Amat.T
            hits = sum(1 for i, (g, r) in enumerate(VALID) if M[i].argmax() == r)
            if hits > (best_combo[0] if best_combo else 0):
                best_combo = (hits, cname, dx, dy, M)
            if hits >= 5:
                print(f'HIT! {cname} dx={dx} dy={dy} hits={hits}/{len(VALID)}')
print('\nbest:', best_combo[0], '/', len(VALID), best_combo[1], 'dx', best_combo[2], 'dy', best_combo[3])
hits, cname, dx, dy, M = best_combo
for i, (g, r) in enumerate(VALID):
    p = M[i].argmax()
    top = np.argsort(M[i])[::-1][:2]
    print(f'{g:5d} -> pred {CHR[p]}({p}) expect {CHR[r]}({r}) {"OK" if p==r else "MISS"} '
          f'top{[(CHR[int(t)], round(float(M[i][t]),3)) for t in top]}')
