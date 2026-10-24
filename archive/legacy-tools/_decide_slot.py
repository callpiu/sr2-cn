# -*- coding: utf-8 -*-
"""决定性实验：用补丁 vf3，按『内存里真实槽位值』直接当 vf3 索引渲染，看是否得到乱码。
内存槽位: 403,1868,454,1067,364,2447,528,356,364,1868,1885,1868,781  (你 的 兄 弟 们 赶 到 他 ...)
期望正确: 你的兄弟们赶到他们的目的地
观测乱码: 你->任 的->璨 弟->偶 兄->巧 们->位 需->雄 要->衡 保->伪 护->该
"""
import sys, os, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp, dxt3_decode
from PIL import Image
import numpy as np

def load(vpp_path):
    v = Vpp(vpp_path)
    vb = v.read(v.find('fnt_chinese', 'vf3_pc'))
    N = struct.unpack('<I', vb[8:12])[0]
    urec = 0xD0 + N * 16
    U = struct.unpack('<%di' % N, vb[urec:urec + N * 4])
    Vb = urec + N * 4
    V = struct.unpack('<%di' % (N - 5), vb[Vb:Vb + (N - 5) * 4])
    pe = v.read(v.find('fnt_chinese', 'g_peg_pc'))
    rgb, alpha = dxt3_decode(pe, 2048, 2048)
    return N, U, V, np.asarray(alpha)

def render(alpha, U, V, indices, cell, path):
    imgs = []
    for k in indices:
        if k >= len(U):
            imgs.append(Image.new('L', (48, 48), 200)); continue
        x = U[k]; y = V[k] if k < len(V) else 0
        a = alpha[y:y+cell, x:x+cell]
        r = 255 - a
        imgs.append(Image.fromarray(r.astype('uint8'), 'L').resize((48, 48), Image.NEAREST))
    canvas = Image.new('L', (48*len(imgs), 48), 255)
    for i, im in enumerate(imgs):
        canvas.paste(im, (i*48, 0))
    canvas.save(path)
    print('saved', path, 'idx', indices)

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
Np, Up, Vp, ap = load(os.path.join(G, 'patch.vpp_pc'))
No, Uo, Vo, ao = load('F:/sr2-cn/pristine/patch.vpp_pc')
print('patch N', Np, 'pristine N', No)

# 内存槽位（兄弟那句）
slots = [403,1868,454,1067,364,2447,528,356,364,1868,1885,1868,781]
print('slots', slots)

# 1) 补丁 vf3 直接按槽位渲染
render(ap, Up, Vp, slots, 31, 'F:/sr2-cn/_D1_patchvf3_slotdirect.png')
# 2) 补丁 vf3 按槽位-0x20
render(ap, Up, Vp, [s-0x20 for s in slots], 31, 'F:/sr2-cn/_D2_patchvf3_slot_minus32.png')
# 3) 原厂 vf3 直接按槽位
render(ao, Uo, Vo, slots, 20, 'F:/sr2-cn/_D3_pristinevf3_slotdirect.png')
# 4) 原厂 vf3 按槽位-0x20
render(ao, Uo, Vo, [s-0x20 for s in slots], 20, 'F:/sr2-cn/_D4_pristinevf3_slot_minus32.png')
