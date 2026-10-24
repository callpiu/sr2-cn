"""解析 Juiced 的松散 .le_strings 文件。

背景
    Mods/JUICED - Strings/ 里有 patch_ch.le_strings / juiced_CH.le_strings 等，
    这些是【松散文件】，Juiced 会让它们覆盖 VPP 内的同名资源。
    之前只查了 static_CH / voice_script_CH / platform_pc_CH，
    漏掉了 patch_ch.le_strings（文件名格式不同：patch_xx 而不是 static_xx）。

本脚本
    1. 解析这些松散文件，列出所有条目（hash + 文本）
    2. 看是否含活动字幕相关文本
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SD = os.path.join(G, "Mods", "JUICED - Strings")

# 从 VPP 取 charlist
from sr2lib import Vpp
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
MAGIC = 0xA84C7F73


def parse(path):
    d = open(path, "rb").read()
    if len(d) < 16:
        return None
    magic, ver, buckets, count = struct.unpack_from("<IHHI", d, 0)
    if magic != MAGIC:
        return ("NOT_LE", magic, ver, buckets, count)
    off_at = 16 + buckets * 8
    offs = [struct.unpack_from("<I", d, off_at + k * 4)[0] for k in range(count)]
    recs = []
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d) - 10):
            continue
        # 文本从 off+8 开始，大端 u16，00 00 结束
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
        recs.append((off, cands, vals))
    return ("OK", buckets, count, recs)


for fn in sorted(os.listdir(SD)):
    if not fn.endswith(".le_strings"):
        continue
    p = os.path.join(SD, fn)
    r = parse(p)
    print("=== %s (%d 字节) ===" % (fn, os.path.getsize(p)))
    if r is None:
        print("  太小")
        continue
    if r[0] == "NOT_LE":
        print("  非 le_strings: magic=0x%08X ver=%d buckets=%d count=%d" % r[1:])
        continue
    _, buckets, count, recs = r
    print("  buckets=%d count=%d 唯一记录=%d" % (buckets, count, len(recs)))
    T = [(S.get(x, "·") for x in vals) for _, _, vals in recs]
    for (off, cands, vals), t in zip(recs, T):
        txt = "".join(t)
        print("    @%-6d %-40s  hash=%s" % (off, txt[:40], "0x%08X" % cands[0] if cands else "-"))
    print()
