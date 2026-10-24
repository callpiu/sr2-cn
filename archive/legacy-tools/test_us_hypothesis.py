"""关键判定：乱码是不是「英文槽位被中文字表/字体解码」的结果？

推理链
    - 已确认：static_CH 里 25 条候选全部打标记后，字幕【仍不变】
      -> 字幕文本的来源【不是】改动的那些 static_CH 记录
    - 但 static_CH 是唯一含活动文本的文件
    - 用户看到的 22 字乱码，长度与 REC2 的中文部分【完全一致】

待检验假设
    H:  游戏实际解码的是【英文文本】（static_US 的 ASCII 槽位），
        但用中文 charlist/字体去渲染 -> ASCII 被当成 CJK 索引 -> 乱码

做法
    取 static_US 里同一个 hash 的记录（英文），把它的槽位拿去用
    charlist_CH 解码，看是否得到「任璨偶巧…」。
    同时也试 charlist_JP / charlist_CZ 等。
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
H1, H2 = 0x84F287ED, 0x10AF1E62
USER = "任璨偶巧位校衡勾远藐乱携伪该亡位通像匪冰挺拮"

v = Vpp(os.path.join(G, "patch.vpp_pc"))
# 各字表
tables = {}
for e in v.entries():
    if e["name"].startswith("charlist_"):
        cps = [int(l) for l in v.read(e).decode("utf-8", "replace").split("\n") if l.strip().isdigit()]
        tables["%s.%s" % (e["name"], e["ext"])] = cps
        print("字表 %-20s %d 项" % (e["name"] + "." + e["ext"], len(cps)))
print()


def get_rec(entry_name, hashwanted):
    d = bytes(v.read(v.find(entry_name, "le_strings")))
    if not d:
        return None
    b, c, oa, offs = file_offsets(d)
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
        if hashwanted in cands:
            u, end = read_units(d, off + 8)
            if u is None:
                continue
            return off, [x for x, _ in u]
    return None


print("=== static_US 里同 hash 的英文记录 ===")
for h, nm in ((H1, "REC1"), (H2, "REC2")):
    r = get_rec("static_US", h)
    if r:
        off, vals = r
        t = "".join(chr(x) for x in vals)
        print("  %s hash 0x%08X @%-9d len=%d" % (nm, h, off, len(vals)))
        print("    英文: %r" % t)
        print("    槽位: %s" % vals[:30])
    else:
        print("  %s 在 static_US 里未找到" % nm)
print()

print("=== 用各字表解码这些英文槽位 ===")
for h, nm in ((H1, "REC1"), (H2, "REC2")):
    r = get_rec("static_US", h)
    if not r:
        continue
    off, vals = r
    print("  %s:" % nm)
    for tn, cps in tables.items():
        S = {i + 0x20: chr(cp) for i, cp in enumerate(cps)}
        t = "".join(S.get(x, "·") for x in vals)
        mark = "  <<< 含乱码字!" if any(c in t for c in "任璨偶巧位雄衡") else ""
        print("      %-20s %s%s" % (tn, t[:46], mark))
    print()

print("=== 反向：把用户乱码的码点当作槽位，看能不能对上英文 ===")
for tn, cps in tables.items():
    S = {i + 0x20: chr(cp) for i, cp in enumerate(cps)}
    # 用户乱码字的码点直接当槽位
    t = "".join(S.get(ord(c), "·") for c in USER)
    print("  %-20s %s" % (tn, t))
