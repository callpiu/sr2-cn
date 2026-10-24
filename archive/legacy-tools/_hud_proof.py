# -*- coding: utf-8 -*-
"""决定性静态实验：common.vpp 的 fnt_chinese (vf3+atlas in textures.vpp)
在索引 k 处的字形，是否 == patch.vpp 图集中「乱码目标字」的字形。
若成立 → 根因 = 引擎用 common 图集 + patch charlist 索引。
"""
import sys, os, struct
sys.path.insert(0, 'F:/sr2-cn')
import numpy as np
from PIL import Image
import sr2lib as S

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
TEX = os.path.join(G, 'textures.vpp_pc')

vp = S.Vpp(os.path.join(G, 'patch.vpp_pc'))
CPS = [int(l) for l in vp.read(vp.find('charlist_CH', 'txt')).decode('utf-8').split('\n') if l.strip().isdigit()]
NP_ = len(CPS)
vf3p = bytes(vp.read(vp.find('fnt_chinese', 'vf3_pc')))
Np = struct.unpack_from('<I', vf3p, 8)[0]
UP = np.array(struct.unpack_from('<%di' % Np, vf3p, 0xD0 + Np * 16), dtype=np.int64)
VP = np.array(struct.unpack_from('<%di' % (Np - 5), vf3p, 0xD0 + Np * 16 + Np * 4), dtype=np.int64)
_, AP = S.dxt3_decode(bytes(vp.read(vp.find('fnt_chinese', 'g_peg_pc'))), 2048, 2048)
AP = np.asarray(AP)
print('patch vf3 N=%d atlas=%s' % (Np, AP.shape))

# common 的 vf3
vc = S.Vpp(os.path.join(G, 'common.vpp_pc'))
vf3c = bytes(vc.read(vc.find('fnt_chinese', 'vf3_pc')))
Nc = struct.unpack_from('<I', vf3c, 8)[0]
UOFF = 0xD0 + Nc * 16
UC = np.array(struct.unpack_from('<%di' % Nc, vf3c, UOFF), dtype=np.int64)
VC = np.array(struct.unpack_from('<%di' % (Nc - 5), vf3c, UOFF + Nc * 4), dtype=np.int64)
print('common vf3 N=%d U[0:5]=%s' % (Nc, UC[:5]))

# common atlas from textures.vpp
def tex_hdr(path):
    with open(path, 'rb') as f:
        d = f.read(5 + 0x14F + 20)
    o = 5 + 0x14F
    num, cs, lo, lf, le = struct.unpack_from('<iiiii', d, o)
    names_at = ((0x800 + lo) & 0xFFFFF800) + 0x800
    ext_at = ((names_at + lf) & 0xFFFFF800) + 0x800
    return num, ((ext_at + le) & 0xFFFFF800) + 0x800, names_at, ext_at

num, ds, names_at, ext_at = tex_hdr(TEX)
with open(TEX, 'rb') as f:
    f.seek(0x800); etab = f.read(num * 28)
    f.seek(names_at); names = f.read(60000)
    f.seek(ext_at); exts = f.read(20000)

def gs(b, o):
    e = b.find(b'\x00', o)
    return b[o:e].decode('ascii', 'replace')

cen = None
for i in range(num):
    a, b, c, d, ln, m1, z = struct.unpack_from('<IIiiiii', etab, i * 28)
    if gs(names, a) == 'fnt_chinese':
        cen = (ds + d, ln); break
print('common atlas cell:', cen)
with open(TEX, 'rb') as f:
    f.seek(cen[0]); atlas_c = f.read(cen[1])
_, AC = S.dxt3_decode(atlas_c, 2048, 2048)
AC = np.asarray(AC)

def pix(img, U, V, i, cell=31):
    x, y = int(U[i]), int(V[i])
    g = img[y:y + 28, x:x + cell]
    o = np.zeros((28, 31), np.float32)
    h, w = min(28, g.shape[0]), min(31, g.shape[1])
    o[:h, :w] = g[:h, :w]
    return o

def score(a, b):
    return float(np.abs(a - b).sum() / (28 * 31 * 255.0))

IDX = {cp: i for i, cp in enumerate(CPS)}
ANCH = [(0x193, 0x4EFB, '你->任'), (0x74C, 0x74A8, '的->璨'),
        (0x42B, 0x5076, '弟->偶'), (0x1C6, 0x5DE7, '兄->巧'),
        (0x16C, 0x4F4D, '们->位'), (0x967, 0x5F1F, '?')]

print('\n=== common[idx] vs patch[乱码目标字idx] L1 距离 ===')
for slot, badcp, label in ANCH:
    tgt = IDX.get(badcp, -1)
    if slot >= Nc or tgt < 0:
        print('  %-8s 越界 slot=%d tgt=%d' % (label, slot, tgt)); continue
    a = pix(AC, UC, VC, slot)
    b = pix(AP, UP, VP, tgt)
    src = slot - 0x20
    c = pix(AP, UP, VP, src) if 0 <= src < Np else np.zeros((28, 31), np.float32)
    print('  %-8s common[%d] vs patch[%s]=%s L1=%.4f | vs patch[%s]=%s(原字) L1=%.4f'
          % (label, slot, tgt, chr(CPS[tgt]), score(a, b), src, chr(CPS[src]) if 0 <= src < NP_ else '?', score(a, c)))

# 反向：common[slot] 最像 patch 里哪个字
print('\n=== common[slot] 在全 patch 表找最佳匹配 ===')
PG = np.stack([pix(AP, UP, VP, i) for i in range(Np)]).reshape(Np, -1)
for slot, badcp, label in ANCH[:5]:
    if slot >= Nc: continue
    a = pix(AC, UC, VC, slot).ravel()
    d = np.abs(PG - a).sum(axis=1) / (28 * 31 * 255.0)
    order = np.argsort(d)[:5]
    print('  %-8s common[%d] -> ' % (label, slot) + '  '.join('%s(%.4f)' % (chr(CPS[k]), d[k]) for k in order))
