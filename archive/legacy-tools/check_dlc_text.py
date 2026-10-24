"""检查 DLC 文本文件是否含活动字幕。

新发现
    DLC/Text/dlc_ch.le_strings (49924 字节) —— DLC 的中文文本表，
    之前完全没查过（只查了 patch.vpp_pc 内的 static_/voice_script_/platform_）。

本脚本
    1. 解析 DLC/Text/ 下所有 .le_strings
    2. 查是否含 hash 0x84F287ED / 0x10AF1E62
    3. 查是否含任何「弟兄们 / 保护 / 袭击」文本
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
H1, H2 = 0x84F287ED, 0x10AF1E62
MAGIC = 0xA84C7F73

v = Vpp(os.path.join(G, "patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}


def parse(path):
    d = open(path, "rb").read()
    if len(d) < 16:
        return None
    magic, ver, buckets, count = struct.unpack_from("<IHHI", d, 0)
    if magic != MAGIC:
        return None
    off_at = 16 + buckets * 8
    offs = [struct.unpack_from("<I", d, off_at + k * 4)[0] for k in range(count)]
    out = []
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d) - 10):
            continue
        vals = []
        i = off + 8
        while i + 1 < len(d):
            b0, b1 = d[i], d[i + 1]
            if b0 == 0 and b1 == 0:
                break
            vals.append((b0 << 8) | b1)
            i += 2
        cands = []
        for base in (0, 4):
            for endian in ("<", ">"):
                if off + base + 4 > len(d):
                    continue
                v0, = struct.unpack_from(endian + "H", d, off + base)
                v1, = struct.unpack_from(endian + "H", d, off + base + 2)
                cands += [(v0 << 16) | v1, (v1 << 16) | v0]
        out.append((off, cands, vals))
    return out


DD = os.path.join(G, "DLC", "Text")
print("=== 解析 DLC/Text/*.le_strings ===")
for fn in sorted(os.listdir(DD)):
    if not fn.endswith(".le_strings"):
        continue
    p = os.path.join(DD, fn)
    recs = parse(p)
    if recs is None:
        print("  %-24s 非 le_strings" % fn)
        continue
    # 查目标 hash 和关键词
    hashhit = []
    keyhit = []
    for off, cands, vals in recs:
        if H1 in cands or H2 in cands:
            hashhit.append((off, cands, vals))
        t = "".join(S.get(x, "·") for x in vals)
        if any(k in t for k in ("弟兄", "袭击", "直升机")):
            keyhit.append((off, t))
    print("  %-24s %5d 记录   hash命中 %d   关键词命中 %d" % (fn, len(recs), len(hashhit), len(keyhit)))
    for off, cands, vals in hashhit:
        t = "".join(S.get(x, "·") for x in vals)
        print("      ★ hash @%-6d %s" % (off, t[:60]))
    for off, t in keyhit[:5]:
        print("      · @%-6d %s" % (off, t[:60]))
