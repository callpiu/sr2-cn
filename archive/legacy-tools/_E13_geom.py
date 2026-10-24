# -*- coding: utf-8 -*-
"""★★ 关键检验：把 vf3 的 U/V 当成【像素坐标】而非【索引】来理解

观察（来自 _E10_layout.py）：
  patch vf3: ASCII 段 U 值 = 1,32,63,94,... 步长 31  ⇒ 这就是【像素列坐标】
            行 0 的 V = 1，行 1 的 V = 32，行距 31
  CJK 段:    U = 1458,1489,1520,... 步长 31， V = 32
  ⇒ U/V 直接是像素坐标！ 图集格 31x31

这解释了为什么"U < 2048、V < 2048"的检查会漏——它们确实都 < 2048。

★ 现在的关键问题：把 (U,V) 当像素坐标，在【官方图集】上取值，
   得到的字形 是否恰好 = 真机观察到的乱码字 ？

再检查：slot=403 -> common.vf3[403] 的 (U,V) = ?
   在该坐标上（官方图集/汉化图集）取值，是哪个字？
"""
import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load_vf3(path):
    v = Vpp(path)
    e = v.find("fnt_chinese", "vf3_pc")
    o = v.data_start + e['body']
    N = struct.unpack_from('<I', v.data, o + 8)[0]
    ro, uo, vo = 0xBC, 0xBC + N*16, 0xBC + N*16 + N*4
    R = [struct.unpack_from('<4H', v.data, o+ro+i*16) for i in range(N)]
    U = [struct.unpack_from('<H', v.data, o+uo+i*2)[0] for i in range(N)]
    V = [struct.unpack_from('<H', v.data, o+vo+i*2)[0] for i in range(N)]
    return R, U, V, N

RC, UC, VC, NC = load_vf3(os.path.join(G, "common.vpp_pc"))
print("common vf3 N=%d" % NC)

vp = Vpp(os.path.join(G, "patch.vpp_pc"))
CL = [int(s) for s in vp.read(vp.find("charlist_CH", "txt")).decode('utf-8').split('\n')
      if s.strip().isdigit()]
c2i = {}
for i, cp in enumerate(CL):
    c2i.setdefault(chr(cp), i)
s2i = {chr(cp): i + 0x20 for i, cp in enumerate(CL)}

CORRECT = "你的弟兄们"
GARBLE  = "任璨偶巧位"

print("\nslot -> common.vf3[idx] 的 (U,V,rec):")
for ch, g in zip(CORRECT, GARBLE):
    sl = s2i[ch]
    print("  %r slot=%-5d idx=%-5d  U=%-5d V=%-5d rec=%s   (乱码 %r idx=%-5d)"
          % (ch, sl, sl, UC[sl], VC[sl], RC[sl], g, c2i[g]))

# 现在：如果我们把 U,V 当"格索引"而非像素，那么 correct
# 引擎可能的算法： glyph_index = V * cols + U  ??  先看 ASCII 段是否自洽
print("\n★ 检验算法: glyph = V * cols + U  (cols=?)\n  ASCII 段应能得到递增下标")
# patch 的 ASCII 段：U=1,32,63,... V=1  => 若 cols=65: 1*65+1=66, 1*65+32=97 ... 不对
# 若 U,V 是像素，则格索引 = (U-1)/31, (V-1)/31
for tag, (R, U, V) in (("patch", load_vf3(os.path.join(G, "patch.vpp_pc"))[:3]),
                       ("common", (RC, UC, VC))):
    print("\n-- %s: 把 U/V 当像素坐标(格距31, 起1) --" % tag)
    for i in (0, 1, 2, 3, 4, 224, 225, 226, 227, 228):
        if i >= len(U): continue
        col = (U[i] - 1) / 31.0
        row = (V[i] - 1) / 31.0
        print("   i=%-4d (U=%4d,V=%4d) -> 格(col=%.2f,row=%.2f)  整数?=%s" % (
            i, U[i], V[i], col, row, col == int(col) and row == int(row)))
