# -*- coding: utf-8 -*-
"""用正确基准（头 0xBC）重新解剖 vf3 记录：16 字节/字形，检查是否有字段携带码点。
patch: record[i] 应能与 charlist[i] 对应；common: record[i] 对应排序码点表。
同时扫 stride=16（记录内字段偏移 0/4/8/12）的锚点数组。"""
import sys, os, struct, re
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
import sr2lib as S

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = S.Vpp(os.path.join(G, "patch.vpp_pc"))
CL = [int(x) for x in re.findall(rb"\d+", vp.read(vp.find("charlist_CH", "txt")))]

def load(vpp, name="fnt_chinese", ext="vf3_pc"):
    v = S.Vpp(os.path.join(G, vpp))
    buf = bytes(v.read(v.find(name, ext)))
    N = struct.unpack_from("<I", buf, 8)[0]
    recs = [struct.unpack_from("<IIII", buf, 0xBC + k * 16) for k in range(N)]
    return buf, N, recs

pbuf, pN, prec = load("patch.vpp_pc")
cbuf, cN, crec = load("common.vpp_pc")

print("=== patch 记录样本（对照 charlist）===")
for i in [0, 1, 2, 32, 33, 90, 94, 95, 96, 100, 330, 331, 332, 336, 354, 362, 371, 391, 422, 967, 1003, 1035, 1784, 2268, 2656]:
    if i < pN:
        print("  patch[%4d] rec=%-28s charlist=%s(%#x)" % (i, prec[i], chr(CL[i]) if CL[i] > 0x20 else "?", CL[i]))

print("\n=== common 记录样本 ===")
for i in [0, 1, 32, 33, 90, 100, 120, 121, 130, 200, 332, 359, 371, 390, 1003, 1158, 1804, 2264, 2635]:
    if i < cN:
        print("  common[%4d] rec=%s" % (i, crec[i]))

# 字段统计
print("\n=== 字段值域统计 ===")
for tag, recs in (("patch", prec), ("common", crec)):
    for f in range(4):
        vals = [r[f] for r in recs]
        nz = sum(1 for v in vals if v != 0)
        print("  %s field%d: 非零=%d/%d  min=%d max=%d  样例=%s"
              % (tag, f, nz, len(vals), min(vals), max(vals), vals[:6]))

# patch field 与 charlist 的相关性
print("\n=== patch 各字段 vs charlist 码点 ===")
for f in range(4):
    same = sum(1 for i in range(pN) if prec[i][f] == CL[i])
    print("  field%d 与 charlist 相同项: %d/%d" % (f, same, pN))

# common: 已知 9 个锚点的字形码点（来自渲染图）
COMMON_CP = {332: 0x4F5C, 359: 0x5012, 371: 0x5065, 390: 0x50CF, 1003: 0x5FD7,
             1158: 0x633D, 1804: 0x76EF, 2264: 0x91CC, 2635: 0x9664}
WRONG = {332: 0x4F4D, 371: 0x4EFB, 391: 0x4F2A, 422: 0x5DE7, 1035: 0x5076,
         1190: 0x8BE5, 1836: 0x74A8, 2296: 0x8861, 2667: 0x96C4}
print("\n=== common 记录字段 vs 已知码点 ===")
for f in range(4):
    same_cp = sum(1 for i, cp in COMMON_CP.items() if crec[i][f] == cp)
    same_wr = sum(1 for i, cp in WRONG.items() if crec[i][f] == cp)
    print("  field%d: 与字形码点相同 %d/9, 与乱码目标码点相同 %d/9" % (f, same_cp, same_wr))
print("\n=== patch 记录字段 vs 乱码目标码点 ===")
for f in range(4):
    same_wr = sum(1 for i, cp in WRONG.items() if prec[i][f] == cp)
    print("  field%d: 与乱码目标相同 %d/9" % (f, same_wr))

# stride 16 扫描两个 vf3（字段偏移 0/4/8/12）
print("\n=== stride16 锚点扫描（vf3 记录内）===")
for tag, buf, N in (("patch", pbuf, pN), ("common", cbuf, cN)):
    for nm, anch in (("WRONG", WRONG), ("COMMON_CP", COMMON_CP)):
        for foff in (0, 4, 8, 12):
            for en in ("<", ">"):
                items = sorted(anch.items())
                i0 = items[0][0]
                base_b = struct.pack(en + "I", items[0][1])
                rest = [((i - i0) * 16 + foff, struct.pack(en + "I", cp)) for i, cp in items[1:]]
                st, hits = 0, 0
                while True:
                    p = buf.find(base_b, st)
                    if p < 0:
                        break
                    st = p + 1
                    if p % 4 != foff % 4:
                        continue
                    if all(buf[p + off:p + off + 4] == b for off, b in rest):
                        hits += 1
                if hits:
                    print("  %s %s field+%d %s: %d 处" % (tag, nm, foff, "LE" if en == "<" else "BE", hits))
print("（无输出=记录内也无锚点数组）")
