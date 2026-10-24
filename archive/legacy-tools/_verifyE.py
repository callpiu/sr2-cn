# -*- coding: utf-8 -*-
"""修复后验证：用【引擎实际路径】渲染直升机活动字幕
   引擎路径 = common.vpp_pc 的 fnt_chinese.vf3_pc(2838) + textures.vpp_pc 的 fnt_chinese(现已=汉化图集)
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
from PIL import Image

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# 2795 字表 -> slot 映射
vp = Vpp(os.path.join(GAME, "patch.vpp_pc"))
cl = [int(s) for s in vp.read(vp.find("charlist_CH", "txt")).decode('utf-8').split('\n')
      if s.strip().isdigit()]
print("charlist_CH 条目 =", len(cl))
c2s = {}
for i, cp in enumerate(cl):
    if cp >= 0x100:
        c2s.setdefault(chr(cp), i + 0x20)

# 引擎字体：common vf3
vc = Vpp(os.path.join(GAME, "common.vpp_pc"))
ec = vc.find("fnt_chinese", "vf3_pc")
co = vc.data_start + ec['body']
uoff = struct.unpack_from('<i', vc.data, co + 0xB8)[0]
voff = struct.unpack_from('<i', vc.data, co + 0xB4)[0]
N = struct.unpack_from('<i', vc.data, co + 8)[0]
print("engine vf3 N =", N, " uOff=%#x vOff=%#x" % (uoff, voff))

def cuv(i):
    return (struct.unpack_from('<i', vc.data, co + uoff + i*4)[0],
            struct.unpack_from('<i', vc.data, co + voff + i*4)[0])

# 引擎图集：textures（已替换）
vt = Vpp(os.path.join(GAME, "textures.vpp_pc"))
et = next(x for x in vt.entries() if x['name'] == 'fnt_chinese')
atlas = vt.read(et)
print("engine atlas md5 =", hashlib.md5(atlas).hexdigest(), "size", len(atlas))
rgb, alp = dxt3_decode(atlas, 2048, 2048)

# ★ 引擎真实路径 = slot 直接作为 vf3 下标（re 反汇编：codepoint→slot 表，slot 索引 vf3）
def glyph(slot):
    if slot >= N:
        return None
    U, V = cuv(slot)
    if U >= 2048 or V >= 2048:
        return None
    return alp[V:V+32, U:U+32]

rows = []
def render(slots, label):
    imgs = []
    for s in slots:
        g = glyph(s)
        imgs.append(g if g is not None else __import__('numpy').zeros((32,32), 'uint8'))
    import numpy as np
    strip = np.hstack([np.pad(x, ((2,2),(2,2))) for x in imgs])
    return strip

import numpy as np
# REC1 的 slot 序列（从 live patch static_CH 解出）
rec1_slots = [403,1868,91,102,111,114,109,97,116,93,91,99,111,108,111,114,58,103,114,101,101,110,93,1067,454,364,91,47,102,111,114,109,97,116,93,2699,2328,403,1868,423,1222]
rec1_cjk = [403,1868,1067,454,364,2699,2328,403,1868,423,1222]

strips = []
strips.append(("REC1 slots 直接索引 vf3", render(rec1_cjk, "a")))
strips.append(("REC1 slots-0x20", render([s-0x20 for s in rec1_cjk], "b")))

W = max(s.shape[1] for _, s in strips)
H = sum(s.shape[0] + 6 for _, s in strips)
canvas = np.full((H, W), 0, 'uint8')
y = 0
labels = []
for lab, s in strips:
    canvas[y:y+s.shape[0], :s.shape[1]] = s
    labels.append((y, lab))
    y += s.shape[0] + 6
Image.fromarray(canvas).save(r"F:\sr2-cn\_E5_afterfix_rec1.png")
print("写出 _E5_afterfix_rec1.png")
for y, lab in labels:
    print("  y=%d  %s" % (y, lab))
