"""方案 D：实机受控实验 —— 用测试串直接读出 HUD 的字形索引映射。

原理
    把活动串 REC1 换成一串【已知 charlist 索引】的字符，游戏截图后
    逐个位置读出「屏幕上的字」，即可得到映射  槽位 s -> 实际显示的字。

选字原则
    - 视觉高度可辨（不易看错）
    - 索引均匀覆盖整个字表（120..2760），便于看出映射规律

用法
    python make_probe.py 1      # 生成 probe1
    python make_probe.py 2      # 生成 probe2（另一组字）
"""
import os, sys, struct

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OUTDIR = r"F:\sr2-cn\_probe"
os.makedirs(OUTDIR, exist_ok=True)

SRC = os.path.join(G, "patch.vpp_pc")
H1 = 0x84F287ED
variant = sys.argv[1] if len(sys.argv) > 1 else "1"

v = Vpp(SRC)
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
IDX = {chr(cp): i for i, cp in enumerate(cn)}

# 按索引均匀采样，选视觉可辨的常用字
picks = []
step = 120 if variant == "1" else 137
start = 120 if variant == "1" else 180
for t in range(start, len(cn), step):
    ch = chr(cn[t])
    if 0x4e00 <= cn[t] <= 0x9fff:
        picks.append((t, ch))
probe = "".join(ch for _, ch in picks)
print("测试串 %s: %s" % (variant, probe))
print("对应索引:  %s" % [i for i, _ in picks])
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
    if H1 in cands:
        u, end = read_units(bytes(d), off + 8)
        target = (off, [x for x, _ in u])
        break
if target is None:
    raise SystemExit("找不到 REC1")

off, vals = target
n = len(vals)
print("REC1 @%d, %d 槽位" % (off, n))

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
out = os.path.join(OUTDIR, "patch_probe%s.vpp_pc" % variant)
open(out, "wb").write(bytes(raw))
print("已写出: %s (%d 字节)" % (out, len(raw)))

v2 = Vpp(out)
d2 = bytes(v2.read(v2.find("static_CH", "le_strings")))
u, _ = read_units(d2, off + 8)
got = [x for x, _ in u]
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
print()
print("复核（字表解码）: %s" % "".join(S.get(x, "·") for x in got))
print("期望 probe:       %s" % probe)
print()
print("=== 对照表（截图后逐行填「实际显示的字」）===")
print("  %-4s %-8s %-6s %s" % ("位置", "槽位", "索引", "字表字"))
for j, s in enumerate(new_slots):
    if s == 0x20:
        continue
    print("  %-4d %-8d %-6d %s" % (j, s, s - 0x20, S.get(s, "?")))
