"""决定性实验：在 static_CH 里【所有候选活动字幕】记录上打标记。

思路
    前两轮只改了两条最可疑的记录（REC1/REC2），屏幕没反应。
    说明真正的来源是【另一条】记录。

    本轮：把 list_activity_cands.py 找出的**全部 31 条候选**
    （长度<=70 且含 保护/弟兄/袭击/生意 的记录）统统改成
    带序号的 ASCII 标记，例如 "MARK-0007"。

    无论屏幕显示哪一条，都会看到 MARK-XXXX，据此立刻定位。

做法
    只改记录【前 9 个槽位】为 "MARK-XXXX"（8 字符 + 1 空格），其余不动。
    这样：
      - 屏幕若显示该记录 -> 一定会看到 MARK-XXXX
      - 未涉及的记录内容基本保留（只坏前 9 个字符）
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(G, "patch.vpp_pc")
OUTDIR = r"F:\sr2-cn\_probe"
os.makedirs(OUTDIR, exist_ok=True)

v = Vpp(SRC)
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}

raw = bytearray(open(SRC, "rb").read())
ent = v.find("static_CH", "le_strings")
body = bytes(v.read(ent))
pos = raw.find(body)
d = bytearray(body)
b, c, oa, offs = file_offsets(bytes(d))

KEYS = ["保护", "弟兄", "袭击", "生意"]
rows = []
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d) - 10):
        continue
    u, end = read_units(bytes(d), off + 8)
    if u is None:
        continue
    vals = [x for x, _ in u]
    t = "".join(S.get(x, "\uFFFD") for x in vals)
    if any(k in t for k in KEYS) and 2 <= len(t) <= 70:
        rows.append((off, len(vals), t))
# 把 REC1/REC2 强制加入（按 hash 定位，最可靠）
H1, H2 = 0x84F287ED, 0x10AF1E62
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
    if H1 in cands or H2 in cands:
        u, end = read_units(bytes(d), off + 8)
        if u is None:
            continue
        vals = [x for x, _ in u]
        t = "".join(S.get(x, "\uFFFD") for x in vals)
        if not any(r[0] == off for r in rows):
            rows.append((off, len(vals), t))

print("将标记 %d 条记录" % len(rows))
print()
for i, (off, n, t) in enumerate(rows):
    mark = "MARK-%04d" % i
    if len(mark) > n:
        continue
    slots = [ord(ch) for ch in mark] + [0x20] * (n - len(mark))
    for j, s in enumerate(slots):
        bp = off + 8 + j * 2
        d[bp] = (s >> 8) & 0xFF
        d[bp + 1] = s & 0xFF
    print("  %-10s @%-9d len=%-4d 原: %s" % (mark, off, n, t[:44]))

assert len(d) == ent["size"]
raw[pos:pos + len(d)] = d
out = os.path.join(OUTDIR, "patch_probe_marks.vpp_pc")
open(out, "wb").write(bytes(raw))
print()
print("已写出: %s (%d 字节)" % (out, len(raw)))

v2 = Vpp(out)
d2 = bytes(v2.read(v2.find("static_CH", "le_strings")))
print()
print("=== 复核前 5 条 ===")
for i, (off, n, t) in enumerate(rows[:5]):
    u, _ = read_units(d2, off + 8)
    print("  @%-9d -> %r" % (off, "".join(chr(x) for x, _ in u)[:40]))
