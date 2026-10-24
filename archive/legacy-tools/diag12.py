# -*- coding: utf-8 -*-
# 对比 fnt_chinese.vf3 内两套字形定位: VFNT records vs U/V 数组
import struct, sys
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, parse_vfnt
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = Vpp(G + r"\patch.vpp_pc")
vf = bytes(vp.read(vp.find("fnt_chinese", "vf3_pc")))
CPS = [int(l) for l in vp.read(vp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
N = len(CPS)
idx_of = {}
for i, c in enumerate(CPS):
    idx_of.setdefault(c, i)

print(f"vf3 size={len(vf)}, count@8={struct.unpack_from('<I', vf, 8)[0]}")
header, recs, tail = parse_vfnt(vf)
print(f"parse_vfnt: recs={len(recs)}, tail={len(tail)} B")
print(f"rec[0]={recs[0]}, rec[1]={recs[1]}")

U = list(struct.unpack_from("<%di" % N, vf, 0xAF6C))
V = list(struct.unpack_from("<%di" % N, vf, 0xDB18))

# rec 结构: (spacing, byteWidth, offset, kerning) — offset 含义?
# 检查 ASCII 区 rec.offset 与 U/V 是否一致
print("\nASCII 区对照 (i, char, rec_spacing, rec_bytew, rec_offset, rec_kern | U, V):")
for i in (0, 1, 10, 33, 65, 94):
    ch = chr(CPS[i]) if CPS[i] < 0x10000 else '?'
    print(f"  i={i} {ch!r}: rec={recs[i]} | U={U[i]} V={V[i]}")

print("\nCJK 区对照:")
for i in (371, 1836, 1035, 422, 332, 391, 1190):
    ch = chr(CPS[i])
    print(f"  i={i} {ch}: rec={recs[i]} | U={U[i]} V={V[i]}")

# 关键: rec[i].offset 若为线性偏移, 换算 x,y 并与 U/V 比
# cell 宽 31+1=32? 试 offset/2048 与 offset%2048 等
print("\n换算尝试 (假设 offset 为行主序像素偏移, cell=32):")
for i, want in ((371, 336), (1836, 1784), (422, 967), (332, 362), (391, 354)):
    off = recs[i][2]
    for cw in (31, 32):
        cols = 2048 // cw
        x = (off % cols) * cw
        y = off // cols
        hit = (x == U[want] and y == V[want])
        if hit:
            print(f"  i={i} off={off} cw={cw}: -> ({x},{y}) == (U[{want}],V[{want}]) ✓✓✓")
print("(无输出=未命中)")
