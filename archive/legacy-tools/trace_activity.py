"""从活动名的 hash 反查数据源。

思路
    屏幕顶部「直升机突击」「已完成停靠」「面包车耐久」这些【显示正确】，
    说明它们的 hash 链是通的。
    底部乱码那行应该来自同一批数据（比如同一活动定义里的 subtitle 字段）。

    做法：找出「直升机突击」这条记录的 hash，
    然后在各 VPP / DLC / exe 里搜这个 hash 的引用，
    定位活动定义所在的数据文件。
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}

d = bytes(v.read(v.find("static_CH", "le_strings")))
b, c, oa, offs = file_offsets(d)

want = "直升机突击"
hits = []
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d) - 10):
        continue
    u, end = read_units(d, off + 8)
    if u is None:
        continue
    t = "".join(S.get(x, "\uFFFD") for x, _ in u)
    if want in t:
        # 头 4 字节可能是 hash
        hdr = d[off:off + 8]
        cands = []
        for base in (0, 4):
            for endian in ("<", ">"):
                if off + base + 4 > len(d):
                    continue
                v0, = struct.unpack_from(endian + "H", d, off + base)
                v1, = struct.unpack_from(endian + "H", d, off + base + 2)
                cands += [(v0 << 16) | v1, (v1 << 16) | v0]
        hits.append((off, t, hdr.hex(" "), cands))

print("=== 「%s」的记录 ===" % want)
for off, t, hdr, cands in hits:
    print("  @%-9d 头: %s" % (off, hdr))
    print("    文本: %s" % t)
    print("    候选 hash: %s" % ["0x%08X" % h for h in cands])
print()

# 用这些 hash 去搜 exe / 其它文件
if hits:
    targets = set()
    for _, _, _, cands in hits:
        targets.update(cands)
    print("=== 在二进制/文本文件里搜这些 hash ===")
    files = []
    for root, dirs, fs in os.walk(G):
        if any(x in root for x in ("_DLSS5_Backup", "reshade-shaders", "_vanilla_test", "_probe", "Juiced\\logs", "CrashDumps")):
            continue
        for f in fs:
            p = os.path.join(root, f)
            try:
                sz = os.path.getsize(p)
                if sz > 200 * 1024 * 1024 or sz < 16:
                    continue
            except Exception:
                continue
            files.append(p)
    print("  扫描 %d 文件..." % len(files))
    pats = []
    for h in targets:
        pats.append(("0x%08X/le" % h, struct.pack("<I", h)))
        pats.append(("0x%08X/be" % h, struct.pack(">I", h)))
    found = 0
    for p in files:
        try:
            dd = open(p, "rb").read()
        except Exception:
            continue
        for nm, q in pats:
            i = dd.find(q)
            if i >= 0:
                print("  ★ %-58s %-14s @0x%X" % (os.path.relpath(p, G), nm, i))
                found += 1
    print("  命中 %d 处" % found)
