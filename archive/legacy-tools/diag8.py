# -*- coding: utf-8 -*-
# 像素级验证：Korea 字体(idx) 的格子 == patch 字体(屏字) 的格子 ?
import struct, sys
import numpy as np
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
CELL = 31

vp = Vpp(G + r"\patch.vpp_pc")
CPS = [int(l) for l in vp.read(vp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
N = len(CPS)
idx_of = {}
for i, c in enumerate(CPS):
    idx_of.setdefault(c, i)

vf = bytes(vp.read(vp.find("fnt_chinese", "vf3_pc")))
print(f"fnt_chinese.vf3 size={len(vf)} magic={vf[:4]!r}")
U = list(struct.unpack_from("<%di" % N, vf, 0xAF6C))
V = list(struct.unpack_from("<%di" % N, vf, 0xDB18))
_, alphaA = dxt3_decode(bytes(vp.read(vp.find("fnt_chinese", "g_peg_pc"))), 2048, 2048)

vc = Vpp(G + r"\common.vpp_pc")
vk = bytes(vc.read(vc.find("fnt_korea", "vf3_pc")))
print(f"fnt_korea.vf3 size={len(vk)} magic={vk[:4]!r}")
# 试 N=(size-0xBC)//8
for hdr in (0xBC, 0xD0):
    rem = len(vk) - hdr
    if rem % 8 == 0:
        nk = rem // 8
        Uk = list(struct.unpack_from("<%di" % nk, vk, hdr))
        Vk = list(struct.unpack_from("<%di" % nk, vk, hdr + 4*nk))
        ok = all(0 <= x < 2048 for x in Uk[:50]) and all(0 <= y < 1024 for y in Vk[:50])
        print(f"  hdr=0x{hdr:X} N={nk} 坐标合理={ok} U[:8]={Uk[:8]} V[:8]={Vk[:8]}")

tk = Vpp(G + r"\textures.vpp_pc")
ek = tk.find("fnt_korea")
rawk = bytes(tk.read(ek))
print(f"textures fnt_korea: size={len(rawk)}")
# 2048x1024 DXT3
_, alphaK = dxt3_decode(rawk, 2048, 1024)

def cellA(i):
    return alphaA[V[i]:V[i]+28, U[i]:U[i]+CELL].astype(np.int16)
def cellK(i):
    return alphaK[Vk[i]:Vk[i]+28, Uk[i]:Uk[i]+CELL].astype(np.int16)

def diff(a, b):
    if a.shape != b.shape: return 9999
    return int(np.abs(a-b).mean())

# 用户报的映射: 真字(slot idx) -> 屏字
pairs = [("你",371,"任"),("的",1836,"璨"),("弟",1035,"偶"),("兄",422,"巧"),
         ("们",332,"位"),("要",2296,"校"),("出",478,"衡"),("去",581,"勾"),
         ("谈",2357,"远"),("笔",1963,"乱"),("生",1792,"携"),("保",391,"伪"),
         ("护",1190,"该"),("他",324,"亡"),("遭",2531,"像"),("袭",2280,"匪"),
         ("击",479,"冰")]
print(f"\n{'真字':>3}{'slotIdx':>8} | {'屏字':>3}{'屏idx':>6} | K[真idx] vs A[屏idx]  K[真] vs A[真]")
hits = 0
for ch, ti, gch in pairs:
    gi = idx_of.get(ord(gch))
    if gi is None:
        print(f"{ch}{ti:>8} | {gch}  屏字不在charlist!"); continue
    try:
        ck = cellK(ti)
    except Exception:
        print(f"{ch}{ti:>8} | K cell 越界"); continue
    d_cross = diff(ck, cellA(gi))
    d_same  = diff(ck, cellA(ti))
    mark = " <<<" if d_cross < 8 else ""
    if d_cross < 8: hits += 1
    print(f"{ch}{ti:>8} | {gch}{gi:>6} | {d_cross:>6}{mark}        {d_same:>6}")
print(f"\n命中 {hits}/{len(pairs)}")
