# -*- coding: utf-8 -*-
"""★★★ 定论实验：乱码到底由 vf3 还是图集决定

四组合渲染 "你的弟兄们需要你的保护"：
  A. 31px网格vf3(补丁) + 汉化图集(patch.g_peg_pc 34034076)
  B. 31px网格vf3(补丁) + 官方图集(textures fnt_chinese 62a57046)
  C. 官方vf3(2838 kerning) + 汉化图集
  D. 官方vf3(2838 kerning) + 官方图集

正确记录起始偏移 = 0xBC（0xBC + N*16 + N*4 + N*4 == size）
"""
import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
RO = 0xBC


def load_vf3_from_bytes(b, label):
    N = struct.unpack_from('<I', b, 8)[0]
    uo = RO + N * 16
    vo = uo + N * 4
    assert vo + N * 4 == len(b), "%s: size mismatch %d vs %d" % (label, vo + N * 4, len(b))
    U = [struct.unpack_from('<I', b, uo + i * 4)[0] for i in range(N)]
    V = [struct.unpack_from('<I', b, vo + i * 4)[0] for i in range(N)]
    return dict(U=U, V=V, N=N, label=label)


def vf3_of(path, label):
    v = Vpp(path)
    e = v.find("fnt_chinese", "vf3_pc")
    b = v.read(e)
    del v
    return load_vf3_from_bytes(b, label)


def atlas_of(path, label):
    v = Vpp(path)
    e = v.find("fnt_chinese", "g_peg_pc")
    if e is None:
        e = next(x for x in v.entries() if x['name'] == 'fnt_chinese')
    b = v.read(e)
    del v
    _, px = dxt3_decode(b, 2048, 2048)
    return px


REF = "F:/sr2-cn/_ref92/黑道圣徒2简体汉化补丁/patch.vpp_pc"
V415 = "F:/sr2-cn/_test_cn_patch/patch.vpp_pc"
OFF = "F:/sr2-cn/SR2_简体中文补丁_v8/backup_original/patch.vpp_pc"
OFFC = "F:/sr2-cn/_backup_F/common.official_20261013_175139.vpp_pc"

print("加载 vf3 ...")
VF_GRID_REF = vf3_of(REF, "基准包 vf3 (30e9da79, 网格)")
VF_GRID_CUR = vf3_of(os.path.join(G, "patch.vpp_pc"), "当前 patch vf3 (dd72f198, 网格)")
VF_OFFICIAL = vf3_of(OFFC, "官方 common vf3 (659ca3fc, 2838 kerning)")
for t in (VF_GRID_REF, VF_GRID_CUR, VF_OFFICIAL):
    print("   %-40s N=%d" % (t['label'], t['N']))

print("加载图集 ...")
A_CN = atlas_of(os.path.join(G, "patch.vpp_pc"), "汉化图集")
A_TEX = atlas_of(os.path.join(G, "textures.vpp_pc"), "官方 textures 图集")
print("   汉化图集 %s  官方图集 %s" % (A_CN.shape, A_TEX.shape))

# charlist (基准包，2795) —— 与当前游戏逐项相同
v = Vpp(REF)
CL = []
for ln in v.read(v.find("charlist_CH", "txt")).replace(b"\r\n", b"\n").split(b"\n"):
    s = ln.strip()
    if s.isdigit():
        CL.append(int(s))
del v
c2s = {chr(cp): i + 0x20 for i, cp in enumerate(CL)}
print("charlist %d 项" % len(CL))

SIZE = 32


def cell(alp, T, s, size=SIZE):
    if s < 0 or s >= len(T['U']):
        return np.zeros((size, size), 'uint8')
    uu, vv = T['U'][s], T['V'][s]
    if uu + size > 2048 or vv + size > 2048:
        return np.zeros((size, size), 'uint8')
    return alp[vv:vv + size, uu:uu + size]


def strip(alp, T, slots, size=SIZE):
    return np.hstack([np.pad(cell(alp, T, s, size), ((2, 2), (2, 2))) for s in slots])


TEXT = "你的弟兄们需要你的保护"
slots = [c2s[ch] for ch in TEXT]
print("文本 %r -> slots %s" % (TEXT, slots))

tests = [
    ("A 网格vf3(基准包30e9da79) + 汉化图集", strip(A_CN, VF_GRID_REF, slots)),
    ("B 网格vf3(基准包30e9da79) + 官方图集", strip(A_TEX, VF_GRID_REF, slots)),
    ("C 网格vf3(当前dd72f198)  + 汉化图集", strip(A_CN, VF_GRID_CUR, slots)),
    ("D 网格vf3(当前dd72f198)  + 官方图集", strip(A_TEX, VF_GRID_CUR, slots)),
    ("E 官方vf3(2838 kerning)  + 汉化图集", strip(A_CN, VF_OFFICIAL, slots)),
    ("F 官方vf3(2838 kerning)  + 官方图集", strip(A_TEX, VF_OFFICIAL, slots)),
]
W = max(t[1].shape[1] for t in tests)
H = sum(t[1].shape[0] + 10 for t in tests) + 10
cv = np.zeros((H, W + 8), 'uint8')
y = 5
for lab, a in tests:
    cv[y:y + a.shape[0], 4:4 + a.shape[1]] = a
    y += a.shape[0] + 10
out = Image.fromarray(cv)
out = out.resize((out.width * 2, out.height * 2), Image.NEAREST)
out.save(r"F:\sr2-cn\_DECIDE_atlas_vs_vf3.png")
print("\n写出 _DECIDE_atlas_vs_vf3.png")
for i, (lab, _) in enumerate(tests):
    print("   行%d: %s" % (i, lab))
