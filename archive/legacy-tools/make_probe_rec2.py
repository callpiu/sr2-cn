"""方案 D 第二版：把测试串写进 REC2（hash 0x10AF1E62）。

第一轮把测试串写进 REC1 后字幕没变，说明屏幕显示的是 REC2。
本轮改 REC2，并把字符位置标注清楚（加分隔符便于对齐）。
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUTDIR = r"F:\sr2-cn\_probe"
os.makedirs(OUTDIR, exist_ok=True)

SRC = os.path.join(G, "patch.vpp_pc")      # 当前部署（含之前的修改）
H2 = 0x10AF1E62

v = Vpp(SRC)
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
IDX = {chr(cp): i for i, cp in enumerate(cn)}

# 均匀采样，索引间距 110（REC2 有 50 槽位，够放 22 个）
picks = []
for t in range(120, len(cn), 110):
    if 0x4e00 <= cn[t] <= 0x9fff:
        picks.append((t, chr(cn[t])))
probe = "".join(ch for _, ch in picks)
print("REC2 测试串: %s" % probe)
print("索引:        %s" % [i for i, _ in picks])
print()

raw = bytearray(open(SRC, "rb").read())
ent = v.find("static_CH", "le_strings")
body = bytes(v.read(ent))
pos = raw.find(body)
d = bytearray(body)
b, c, oa, offs = file_offsets(bytes(d))

target = None
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
    if H2 in cands:
        u, end = read_units(bytes(d), off + 8)
        target = (off, [x for x, _ in u])
        break
if target is None:
    raise SystemExit("找不到 REC2")

off, vals = target
n = len(vals)
print("REC2 @%d, %d 槽位" % (off, n))

if len(probe) > n:
    probe = probe[:n]
new_slots = [IDX[ch] + 0x20 for ch in probe] + [0x20] * (n - len(probe))
assert len(new_slots) == n

for j, s in enumerate(new_slots):
    bp = off + 8 + j * 2
    d[bp] = (s >> 8) & 0xFF
    d[bp + 1] = s & 0xFF

assert len(d) == ent["size"]
raw[pos:pos + len(d)] = d
out = os.path.join(OUTDIR, "patch_probe_rec2.vpp_pc")
open(out, "wb").write(bytes(raw))
print("已写出: %s" % out)

v2 = Vpp(out)
d2 = bytes(v2.read(v2.find("static_CH", "le_strings")))
u, _ = read_units(d2, off + 8)
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
print()
print("复核: %s" % "".join(S.get(x, "·") for x, _ in u))
print()
print("=== 对照表 ===")
print("  %-4s %-8s %-6s %s" % ("位置", "槽位", "索引", "字表字"))
for j, s in enumerate(new_slots):
    if s == 0x20:
        continue
    print("  %-4d %-8d %-6d %s" % (j, s, s - 0x20, S.get(s, "?")))
