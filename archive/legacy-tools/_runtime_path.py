# -*- coding: utf-8 -*-
"""真机渲染路径复现：common.vpp 的 fnt_chinese.vf3_pc + textures.vpp 的 fnt_chinese atlas。
把 REC2 的 slot 按「引擎实际用的索引」渲染，找出正确的索引公式。
引擎实际索引候选：
  A) idx = slot            (直接当 common vf3 索引)
  B) idx = slot - 0x20     (charlist idx)
比较渲染结果与真实文本 "你的弟兄们要出去谈几笔生意，保护他们免遭袭击"。
"""
import sys, os, struct
sys.path.insert(0, 'F:/sr2-cn')
import numpy as np
import sr2lib as S
from PIL import Image

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
vp = S.Vpp(os.path.join(G, 'patch.vpp_pc'))
CPS = [int(l) for l in vp.read(vp.find('charlist_CH', 'txt')).decode('utf-8').split('\n') if l.strip().isdigit()]

# common vf3
vc = S.Vpp(os.path.join(G, 'common.vpp_pc'))
vf3c = bytes(vc.read(vc.find('fnt_chinese', 'vf3_pc')))
Nc = struct.unpack_from('<I', vf3c, 8)[0]
UOFF = 0xD0 + Nc * 16
UC = np.array(struct.unpack_from('<%di' % Nc, vf3c, UOFF), dtype=np.int64)
VC = np.array(struct.unpack_from('<%di' % (Nc - 5), vf3c, UOFF + Nc * 4), dtype=np.int64)
print('common vf3 N=%d' % Nc)

# textures atlas
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
print('textures atlas', AC.shape)

def strip(img, U, V, idxs, path, c=31):
    imgs = []
    for i in idxs:
        if not (0 <= i < len(U) and 0 <= i < len(V)):
            imgs.append(Image.new('L', (42, 42), 100)); continue
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
    print('saved', path)

rec2_slots = [403, 1868, 1067, 454, 364, 2328, 510, 613, 2389, 502, 1995, 1824, 1159, 2822, 423, 1222, 356, 364, 460, 2563, 2312, 511]
print('真实文本:', '你的弟兄们要出去谈几笔生意，保护他们免遭袭击')
strip(AC, UC, VC, rec2_slots, 'F:/sr2-cn/_H1_ctex_slot.png')
strip(AC, UC, VC, [s - 0x20 for s in rec2_slots], 'F:/sr2-cn/_H2_ctex_slotm32.png')
# 也试 idx = slot + 0x20
strip(AC, UC, VC, [s + 0x20 for s in rec2_slots], 'F:/sr2-cn/_H3_ctex_slotp32.png')
print('candidates done')
