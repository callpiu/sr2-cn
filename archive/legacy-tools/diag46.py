# -*- coding: utf-8 -*-
# diag46: 匹配管线自检 + B 是否按新序排列的对照实验
import sys, struct, random
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
grayB = rgbB.mean(axis=2)

W, H = 20, 28

def nf(x):
    x = np.asarray(x, np.float32).flatten()
    x = x - x.mean()
    n = np.linalg.norm(x)
    return x / n if n > 0 else x

def down(c, sw):
    return c[:, (np.arange(W) * sw // W)]

Amat = np.array([nf(down(alA[pV[g]:pV[g] + H, pU[g]:pU[g] + 31], 31)) for g in range(N)])

# self-test
pred = int((Amat @ Amat[371]).argmax())
print('A self-test: A@371 nearest =', CHR[pred], '(expect 你)')

# control: B@g nearest in A
random.seed(2)
ok, tot, sims = 0, 0, []
for g in random.sample(range(50, 2700), 25):
    cell = grayB[cV[g]:cV[g] + H, cU[g]:cU[g] + 18]
    if cell.shape != (H, 18):
        continue
    v = Amat @ nf(down(cell, 18))
    p = int(v.argmax())
    tot += 1
    if p == g:
        ok += 1
    sims.append((g, CHR[g], '->', CHR[p], p, round(float(v.max()), 3)))
print('B@g vs A control hits:', ok, '/', tot)
for s in sims:
    print(' ', s)
