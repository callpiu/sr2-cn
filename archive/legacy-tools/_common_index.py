# -*- coding: utf-8 -*-
"""定案 common 字体索引关系：common[i] 画的是哪个 charlist 字。
上面图证实 common[i-32] == charlist[i]，即 common[j] == 某个字。
反推：common[j] 画的是 charlist 中的哪一项？
做法：用 patch 图集（其 idx==charlist idx 已证）跟 common 图集逐格比对 —— 但两图集排布不同。
改用「与 common 同索引的 patch idx」：图中 row1=patch[idx], row2=common[idx]。
观察 row2 '何佛作你佩佳使來' vs row1 '以仪们仰件价任份' —— 不同。
而 row3=common[idx-32] == row1 的 charlist 名 = charlist[idx]。
=> 引擎正确用法 = common[charlist_idx]；但引擎实际用的是 common[slot] = common[charlist_idx+32]。
验证：common[371+32]=common[403] 应画 charlist[371+32]=charlist[403] 的字。
"""
import sys, os, struct
sys.path.insert(0, 'F:/sr2-cn')
import numpy as np
import sr2lib as S
from PIL import Image

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
vp = S.Vpp(os.path.join(G, 'patch.vpp_pc'))
CPS = [int(l) for l in vp.read(vp.find('charlist_CH', 'txt')).decode('utf-8').split('\n') if l.strip().isdigit()]
Np = struct.unpack_from('<I', bytes(vp.read(vp.find('fnt_chinese', 'vf3_pc'))), 8)[0]
vf3p = bytes(vp.read(vp.find('fnt_chinese', 'vf3_pc')))
UP = np.array(struct.unpack_from('<%di' % Np, vf3p, 0xD0 + Np * 16))
VP = np.array(struct.unpack_from('<%di' % (Np - 5), vf3p, 0xD0 + Np * 16 + Np * 4))
_, AP = S.dxt3_decode(bytes(vp.read(vp.find('fnt_chinese', 'g_peg_pc'))), 2048, 2048)
AP = np.asarray(AP)
vc = S.Vpp(os.path.join(G, 'common.vpp_pc'))
vf3c = bytes(vc.read(vc.find('fnt_chinese', 'vf3_pc')))
Nc = struct.unpack_from('<I', vf3c, 8)[0]
UC = np.array(struct.unpack_from('<%di' % Nc, vf3c, 0xD0 + Nc * 16))
VC = np.array(struct.unpack_from('<%di' % (Nc - 5), vf3c, 0xD0 + Nc * 16 + Nc * 4))

def tex_hdr(path):
    with open(path, 'rb') as f:
        d = f.read(5 + 0x14F + 20)
    o = 5 + 0x14F
    num, cs, lo, lf, le = struct.unpack_from('<iiiii', d, o)
    na = ((0x800 + lo) & 0xFFFFF800) + 0x800
    ea = ((na + lf) & 0xFFFFF800) + 0x800
    return num, ((ea + le) & 0xFFFFF800) + 0x800, na, ea

TEX = os.path.join(G, 'textures.vpp_pc')
num, ds, na, ea = tex_hdr(TEX)
with open(TEX, 'rb') as f:
    f.seek(0x800); et = f.read(num * 28)
    f.seek(na); nm = f.read(60000)
    f.seek(ea); ex = f.read(20000)

def gs(b, o):
    e = b.find(b'\x00', o)
    return b[o:e].decode('ascii', 'replace')

cen = None
for i in range(num):
    a, b, c, d, ln, m1, z = struct.unpack_from('<IIiiiii', et, i * 28)
    if gs(nm, a) == 'fnt_chinese':
        cen = (ds + d, ln); break
with open(TEX, 'rb') as f:
    f.seek(cen[0]); ac = f.read(cen[1])
_, AC = S.dxt3_decode(ac, 2048, 2048)
AC = np.asarray(AC)

def strip(img, U, V, idxs, path, c=31):
    imgs = []
    for i in idxs:
        x, y = int(U[i]), int(V[i])
        g = img[y:y + 28, x:x + c]
        o = np.zeros((28, 31), np.float32)
        h, w = min(28, g.shape[0]), min(31, g.shape[1])
        o[:h, :w] = g[:h, :w]
        imgs.append(Image.fromarray((255 - o).astype('uint8'), 'L').resize((42, 42), Image.NEAREST))
    cv = Image.new('L', (42 * len(imgs), 42), 255)
    for i, im in enumerate(imgs):
        cv.paste(im, (i * 42, 0))
    cv.save(path)
    print('saved', path, 'idx', idxs)

# 关键验证：common[slot] (slot=403,1868,454,1067,364) 画的字 = charlist[slot]
slots = [403, 1868, 454, 1067, 364, 2447, 528, 356]
print('common[slot] 索引:', slots)
print('  charlist[slot] 应为:', ''.join(chr(CPS[s]) for s in slots))
strip(AC, UC, VC, slots, 'F:/sr2-cn/_G1_common_at_slot.png')
print('charlist[idx=slot-32]:', ''.join(chr(CPS[s-32]) for s in slots))
strip(AC, UC, VC, [s - 32 for s in slots], 'F:/sr2-cn/_G2_common_at_idx.png')
print('charlist 原文本: 你的兄弟们赶到他')
print('patch[idx=slot-32]:')
strip(AP, UP, VP, [s - 32 for s in slots], 'F:/sr2-cn/_G3_patch_at_idx.png')
