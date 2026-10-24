# -*- coding: utf-8 -*-
"""★★★ 定论：common.vf3 的 U 数组 = 【字距/kerning 表】，不是图集列坐标
          patch.vf3 的 U 数组 = 【图集列坐标】（步长 31，与两张图集的 31 格完全一致）

证据：
  common U 唯一值 307 个，最小间隔 1px，范围 1..2023
  patch  U 唯一值 65 个，固定间隔 31          ← 65 列 = 2048/31 = 66 → 65 列可用
  两图集实际格距都是 31（列块起点间隔 31）

⇒ 引擎流程（由 0x7F4EE0 / 0x7F4F20 反汇编）：
     codepoint --(查字表)--> slot --(vf3[slot].U/V)--> 图集像素坐标
  ★ 若引擎读的是 common.vpp_pc 的 vf3，则拿到的是【字距】当【列坐标】
  ★ 若引擎读 patch.vpp_pc 的 vf3，则拿到正确的【列坐标】

⇒ 乱码 = 引擎用 common.vf3 的"字距值"去当列坐标索引 31px 网格 ⇒ 取到完全无关的格子。
   这也解释了 why 不是简单平移，而是"乱序映射"。
"""
import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load(path):
    v = Vpp(path); e = v.find("fnt_chinese", "vf3_pc"); o = v.data_start + e['body']
    N = struct.unpack_from('<I', v.data, o + 8)[0]
    ro = 0xBC; uo = ro + N*16; vo = uo + N*4
    R = [struct.unpack_from('<4H', v.data, o+ro+i*16) for i in range(N)]
    U = [struct.unpack_from('<I', v.data, o+uo+i*4)[0] for i in range(N)]
    V = [struct.unpack_from('<I', v.data, o+vo+i*4)[0] for i in range(N)]
    return R, U, V, N

RP, UP, VP, NP = load(os.path.join(G, "patch.vpp_pc"))
RC, UC, VC, NC = load(os.path.join(G, "common.vpp_pc"))

print("★ common vf3 的 rec(前两字段) vs U 值：")
print("  若 rec[0],rec[1] 是左右 bearing 而 U 是累计列坐标，则 U 应约等于前面所有 rec0 之和")
acc = 0
for i in range(0, 12):
    print("  i=%-3d rec=%s U=%-5d acc=%d" % (i, RC[i], UC[i], acc))
    acc += RC[i][0]

print("\n★ patch vf3：")
for i in range(0, 6):
    print("  i=%-3d rec=%s U=%-5d V=%-5d" % (i, RP[i], UP[i], VP[i]))

print("\n★ 用 common 的前缀和 检验 U == cumsum(rec[0]):")
acc = 0; hits = 0
for i in range(0, 300):
    if UC[i] == acc: hits += 1
    acc += RC[i][0]
print("   命中 %d/300" % hits)

print("\n★ 用 patch 检验 U == cumsum(rec[0])？")
acc = 0; hits = 0
for i in range(0, 300):
    if UP[i] == acc: hits += 1
    acc += RP[i][0]
print("   命中 %d/300" % hits)

# ★ 直接验证：把 common.vf3 的 V 当行、U 当"像素列" 去官方图集取图（前面已看是乱码）
#   现在反过来：**用 patch.vf3 的坐标 + 官方图集**（因为引擎可能加载 patch vf3 但图集来自 textures）
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
AH = vp.read(vp.find("fnt_chinese", "g_peg_pc"))
vt = Vpp(os.path.join(G, "textures.vpp_pc"))
AT = vt.read(next(x for x in vt.entries() if x['name'] == 'fnt_chinese'))
_, PH = dxt3_decode(AH, 2048, 2048)
_, PT = dxt3_decode(AT, 2048, 2048)

CL = [int(s) for s in vp.read(vp.find("charlist_CH", "txt")).decode('utf-8').split('\n') if s.strip().isdigit()]
c2s = {chr(cp): i + 0x20 for i, cp in enumerate(CL)}
TARGET = "你的弟兄们需要你的保护"
slots = [c2s[c] for c in TARGET]

def strip(alp, U, V, slots, size=32):
    out = []
    for s in slots:
        if s >= len(U): out.append(np.zeros((size,size),'uint8')); continue
        uu, vv = U[s], V[s]
        if uu+size > 2048 or vv+size > 2048: out.append(np.zeros((size,size),'uint8')); continue
        out.append(alp[vv:vv+size, uu:uu+size])
    return np.hstack([np.pad(x, ((2,2),(2,2))) for x in out])

rows = [
    ("patch.vf3 + patch图集",  strip(PH, UP, VP, slots)),
    ("patch.vf3 + tex官方图集", strip(PT, UP, VP, slots)),
    ("common.vf3 + patch图集",  strip(PH, UC, VC, slots)),
    ("common.vf3 + tex官方图集",strip(PT, UC, VC, slots)),
]
W = max(r[1].shape[1] for r in rows); H = sum(r[1].shape[0]+12 for r in rows)+8
cv = np.zeros((H, W+8), 'uint8'); y = 4
for lab, a in rows:
    cv[y:y+a.shape[0], 4:4+a.shape[1]] = a; y += a.shape[0]+12
Image.fromarray(cv).save(r"F:\sr2-cn\_E21_verdict.png")
print("\n写出 _E21_verdict.png")
for i,(l,_) in enumerate(rows): print("  行%d %s" % (i,l))
