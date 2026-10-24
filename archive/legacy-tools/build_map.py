"""构建「HUD 实际渲染」映射表：用已知的乱码样本反推。

已知样本（用户抄录，位置对齐）：
  REC1 应为: 弟兄们需要你的保护
  实际显示:  任璨偶巧位雄衡[任璨伪该]

注意用户的记录里 REC1 出现了重复的「任璨」（第 1、2 位和第 7、8 位），
这与「弟兄们需要你的保护」对不上（第 7、8 位应是「你、的」）。
所以可能：
  (a) 用户抄录时把两个串混在一起了
  (b) 显示的其实是【另一条】字符串

本脚本：
  1. 列出 static_CH 里所有 hash 的记录数（看有没有重复定义）
  2. 检查 REC1/REC2 是否在多个文件里都有定义（static_CH / platform_pc_CH / voice_script_CH）
  3. 把「弟兄们需要你的保护」和「弟兄们要出去谈几笔生意，保护他们免遭袭击」
     在【所有可能的字表】(charlist_CH / charlist_JP / charlist_CZ / charlist_PL / charlist_RU / charlist_SK)
     下解码，看哪个能产出「任璨偶巧位雄衡…」
"""
import os, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
H1, H2 = 0x84F287ED, 0x10AF1E62
v = Vpp(os.path.join(G, "patch.vpp_pc"))

# 所有字表
tables = {}
for e in v.entries():
    if e["name"].startswith("charlist_"):
        raw = v.read(e).decode("utf-8", "replace")
        cps = [int(l) for l in raw.split("\n") if l.strip().isdigit()]
        tables["%s.%s" % (e["name"], e["ext"])] = cps
        print("字表 %-22s %d 项" % (e["name"] + "." + e["ext"], len(cps)))
print()

# 收集所有 le_strings 里这两个 hash 的定义
def find_hash_entries(vpp, h1, h2):
    out = []
    for e in vpp.entries():
        if e["ext"] not in ("le_strings", ""):
            continue
        d = bytes(vpp.read(e))
        try:
            b, c, oa, offs = file_offsets(d)
        except Exception:
            continue
        for off in dict.fromkeys(offs):
            if not (0 < off <= len(d) - 10):
                continue
            cands = []
            for base in (0, 4):
                for endian in ("<", ">"):
                    if off + base + 4 > len(d):
                        continue
                    v0, = struct.unpack_from(endian + "H", d, off + base)
                    v1, = struct.unpack_from(endian + "H", d, off + base + 2)
                    cands += [(v0 << 16) | v1, (v1 << 16) | v0]
            h = h1 if h1 in cands else (h2 if h2 in cands else None)
            if h is None:
                continue
            u, end = read_units(d, off + 8)
            if u is None:
                continue
            out.append((e["name"], h, off, [x for x, _ in u]))
    return out

defs = find_hash_entries(v, H1, H2)
print("=== 这两个 hash 在 patch.vpp_pc 里的全部定义 ===")
for name, h, off, vals in defs:
    print("  %-18s hash 0x%08X @%-9d len=%d" % (name, h, off, len(vals)))
print()

print("=== 用各字表解码这些槽位 ===")
for name, h, off, vals in defs:
    print("  %s hash 0x%08X:" % (name, h))
    for tname, cps in tables.items():
        S = {i + 0x20: chr(cp) for i, cp in enumerate(cps)}
        t = "".join(S.get(x, "·") for x in vals)
        mark = ""
        if any(ch in t for ch in "任璨偶巧位雄衡"):
            mark = "   <<< 命中乱码字！"
        print("      %-22s %s%s" % (tname, t[:46], mark))
    print()

print("=== 目标乱码字在各字表里的索引 ===")
targets = "任璨偶巧位雄衡伪该"
for tname, cps in tables.items():
    IDX = {chr(cp): i for i, cp in enumerate(cps)}
    idxs = [IDX.get(ch, -1) for ch in targets]
    print("  %-22s %s" % (tname, idxs))
print()
print("=== 期望字在各字表里的索引 ===")
wants = "弟兄们需要你的保护"
for tname, cps in tables.items():
    IDX = {chr(cp): i for i, cp in enumerate(cps)}
    idxs = [IDX.get(ch, -1) for ch in wants]
    print("  %-22s %s" % (tname, idxs))
