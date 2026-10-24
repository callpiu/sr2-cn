# -*- coding: utf-8 -*-
"""vf3 记录结构解剖：16 字节/字形里是否藏码点？

patch 的 charlist_CH 已知（2795 项），可作标定：若 vf3 记录某字段 == charlist_CH[k]，
则 common 的 vf3 同字段就是 common 的字表 -> 直接解出全部映射。
"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import sr2lib as S

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

vp = S.Vpp(os.path.join(G, "patch.vpp_pc"))
CPS = [int(l) for l in vp.read(vp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
vf3p = bytes(vp.read(vp.find("fnt_chinese", "vf3_pc")))
NP_ = len(CPS)
print("[patch] charlist %d 项, vf3 %d 字节" % (NP_, len(vf3p)))
print("  vf3 头 32 字节: %s" % " ".join("%02X" % c for c in vf3p[:32]))
print("  count@8 = %d" % struct.unpack_from("<I", vf3p, 8)[0])

print("\n=== patch vf3 前 12 条记录 vs charlist_CH ===")
print("  %-4s %-22s %-10s %s" % ("k", "record(4xu32)", "charlist", "字段匹配"))
for k in range(12):
    o = 0xD0 + k * 16
    r = struct.unpack_from("<IIII", vf3p, o)
    cp = CPS[k]
    hit = [j for j in range(4) if r[j] == cp]
    print("  %-4d %-22s U+%04X %-8s %s" % (k, str(r), cp, chr(cp) if 32 <= cp < 127 else "",
          "字段%d=%d★" % (hit[0], r[hit[0]]) if hit else ""))

# 全表统计：哪个字段与 charlist 完全一致
print("\n=== 全表字段一致性统计（patch, %d 项）===" % NP_)
for j, nm in enumerate(["f0", "f1", "f2", "f3"]):
    same = 0
    for k in range(NP_):
        r = struct.unpack_from("<I", vf3p, 0xD0 + k * 16 + j * 4)[0]
        if r == CPS[k]:
            same += 1
    print("  %s 与 charlist_CH 完全相同: %d / %d" % (nm, same, NP_))

# common
vpc = S.Vpp(os.path.join(G, "common.vpp_pc"))
ec = None
for e in vpc.entries():
    if e["name"].lower() == "fnt_chinese" and e["ext"].lower() == "vf3_pc":
        ec = e; break
vf3c = bytes(vpc.read(ec))
NC_ = struct.unpack_from("<I", vf3c, 8)[0]
print("\n[common] vf3 %d 字节, count@8 = %d" % (len(vf3c), NC_))
print("  vf3 头 32 字节: %s" % " ".join("%02X" % c for c in vf3c[:32]))
print("\n=== common vf3 前 12 条记录 ===")
for k in range(12):
    o = 0xD0 + k * 16
    r = struct.unpack_from("<IIII", vf3c, o)
    print("  %-4d %s" % (k, str(r)))

# 检查 common 各字段是否像「码点」（落在 CJK 区且递增）
print("\n=== common 各字段是否码点状（前300项单调性/范围）===")
for j, nm in enumerate(["f0", "f1", "f2", "f3"]):
    vals = [struct.unpack_from("<I", vf3c, 0xD0 + k * 16 + j * 4)[0] for k in range(300)]
    inc = sum(1 for a, b in zip(vals, vals[1:]) if b > a)
    inr = sum(1 for v in vals if 0x4E00 <= v <= 0x9FFF)
    print("  %s: 递增 %d/299, 落在CJK区 %d/300, 范围 %d~%d" % (nm, inc, inr, min(vals), max(vals)))

# 尾部结构
print("\n=== common vf3 尾部（记录区之后）===")
tail_off = 0xD0 + NC_ * 16
print("  记录区结束于 0x%X, 剩余 %d 字节" % (tail_off, len(vf3c) - tail_off))
t = vf3c[tail_off:tail_off + 64]
print("  尾部前 64 字节: %s" % " ".join("%02X" % c for c in t))
