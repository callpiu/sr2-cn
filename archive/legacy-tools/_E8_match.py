# -*- coding: utf-8 -*-
"""★ 决定性实验：用【汉化图集自身的 U/V】+ common vf3 的【字形描述】
   检验 汉化图集(v514已部署) 与 charlist_CH 的 slot 索引 是否配套。

   若配套：以 common vf3 的 rec.width=29(V) 与 U=0 去索引，应得正确字形
   若不配套：横向严重拉伸

   另：直接对比两张表在相同下标下的 U/V 值差异 —— 这是"匹配性"的硬指标。
"""
import sys, os, struct
import numpy as np
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load(path, name, ext):
    v = Vpp(path)
    e = v.find(name, ext)
    o = v.data_start + e['body']
    N = struct.unpack_from('<I', v.data, o + 8)[0]
    ro = 0xBC
    uo = ro + N*16
    vo = uo + N*4
    R = [struct.unpack_from('<4H', v.data, o+ro+i*16) for i in range(N)]
    U = [struct.unpack_from('<H', v.data, o+uo+i*2)[0] for i in range(N)]
    V = [struct.unpack_from('<H', v.data, o+vo+i*2)[0] for i in range(N)]
    return dict(N=N, R=R, U=U, V=V, size=e['size'])

c = load(os.path.join(GAME, "common.vpp_pc"), "fnt_chinese", "vf3_pc")
p = load(os.path.join(GAME, "patch.vpp_pc"),  "fnt_chinese", "vf3_pc")
print("common N=%d size=%d | patch N=%d size=%d" % (c['N'], c['size'], p['N'], p['size']))

print("\n== 下标 0..5 ==  common(U,V,w_left,w_right,top,bot)  vs  patch(...)")
for i in range(6):
    print("  %2d  c=(%4d,%4d,%3d,%3d,%3d,%3d)   p=(%4d,%4d,%3d,%3d,%3d,%3d)" % (
        i, c['U'][i], c['V'][i], *c['R'][i], p['U'][i], p['V'][i], *p['R'][i]))

print("\n== CJK 段（下标 224..235） ==")
for i in range(224, 236):
    print("  %3d  c=(%4d,%4d,%3d,%3d)   p=(%4d,%4d,%3d,%3d)" % (
        i, c['U'][i], c['V'][i], *c['R'][i][:2], p['U'][i], p['V'][i], *p['R'][i][:2]))

# 匹配性硬指标：同一 CJK 下标，patch 的 V（行号）应 = 该字在汉化图集里的行
# 而 common 的 V 应 = 同一字在官方图集里的行。若两者不同 ⇒ 表结构与图集无关，纯靠下标对齐。
diffU = sum(1 for i in range(min(c['N'], p['N'])) if c['U'][i] != p['U'][i])
diffV = sum(1 for i in range(min(c['N'], p['N'])) if c['V'][i] != p['V'][i])
diffR = sum(1 for i in range(min(c['N'], p['N'])) if c['R'][i] != p['R'][i])
print("\n== 下标 0..%d 逐项差异: U差 %d, V差 %d, rec差 %d ==" % (min(c['N'],p['N'])-1, diffU, diffV, diffR))

# 渲染验证：用【patch 自己的 U/V】+ 汉化图集 ⇒ 应为完美字形
vp = Vpp(os.path.join(GAME, "patch.vpp_pc"))
atlas_han = vp.read(vp.find("fnt_chinese", "g_peg_pc"))
_, AH = dxt3_decode(atlas_han, 2048, 2048)
vt = Vpp(os.path.join(GAME, "textures.vpp_pc"))
atlas_cur = vt.read(next(x for x in vt.entries() if x['name']=='fnt_chinese'))
_, AC = dxt3_decode(atlas_cur, 2048, 2048)

TARGET = "你的弟兄们需要你的保护"
# 字表 -> slot
cl = [int(s) for s in vp.read(vp.find("charlist_CH","txt")).decode('utf-8').split('\n') if s.strip().isdigit()]
c2s = {}
for i, cp in enumerate(cl):
    if cp >= 0x100: c2s.setdefault(chr(cp), i + 0x20)

def draw(alp, U, V, slots, size=30):
    cells = []
    for s in slots:
        if s >= len(U): cells.append(np.zeros((size,size),'uint8')); continue
        uu, vv = U[s], V[s]
        if uu+size > 2048 or vv+size > 2048: cells.append(np.zeros((size,size),'uint8')); continue
        cells.append(alp[vv:vv+size, uu:uu+size])
    return np.hstack([np.pad(x, ((2,2),(2,2))) for x in cells])

slots = [c2s[ch] for ch in TARGET]
print("\n'%s' 的 slot:" % TARGET, slots)

import numpy as np
from PIL import Image
IM = []
def add(alp, U, V, lab):
    a = draw(alp, U, V, slots); b = draw(alp, U, V, [s-0x20 for s in slots])
    IM.append((lab+" (slot)", a)); IM.append((lab+" (slot-0x20)", b))

add(AH, p['U'], p['V'], "汉化图集+patch表")
add(AH, c['U'], c['V'], "汉化图集+common表")
add(AC, c['U'], c['V'], "当前已部署图集+common表")

W = max(x[1].shape[1] for x in IM); H = sum(x[1].shape[0]+8 for x in IM)
cv = np.zeros((H+8, W+300), 'uint8'); y = 4
for lab, a in IM:
    cv[y:y+a.shape[0], 300:300+a.shape[1]] = a
    y += a.shape[0]+8
Image.fromarray(cv).save(r"F:\sr2-cn\_E8_match_test.png")
print("写出 _E8_match_test.png（4 行 x 2 段：上=slot 下=slot-0x20）")
print("行序: 1 汉化图集+patch表 / 2 汉化图集+common表 / 3 当前部署图集+common表")
