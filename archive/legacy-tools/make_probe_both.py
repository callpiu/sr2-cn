"""方案 D 第三版：两条串【同时】替换成 ASCII 长串。

为什么这么做
    前两轮分别测 REC1 / REC2，屏幕显示的乱码都没变。
    可能原因：屏幕显示的是【另一条】串，或者字幕走了不同的文本源。

    本轮把 REC1 和 REC2 都换成 ASCII 文本。
      - 若字幕变英文  -> 屏幕确实用这两条之一，且 ASCII 可渲染（保底修复成立）
      - 若字幕仍乱码  -> 屏幕用的是完全不同的文本源，需要换思路

    ASCII 在这里是安全的：游戏所有英文界面渲染都正常。
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
H1, H2 = 0x84F287ED, 0x10AF1E62
TXT = {
    H1: "PROBE-A HOMIES PROTECTION",
    H2: "PROBE-B HOMIES DEALS PROTECT THEM",
}

raw = bytearray(open(SRC, "rb").read())
v = Vpp(SRC)
ent = v.find("static_CH", "le_strings")
body = bytes(v.read(ent))
pos = raw.find(body)
d = bytearray(body)
b, c, oa, offs = file_offsets(bytes(d))

plan = []
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
    h = H1 if H1 in cands else (H2 if H2 in cands else None)
    if h is None:
        continue
    u, end = read_units(bytes(d), off + 8)
    if u is None:
        continue
    plan.append((h, off, [x for x, _ in u]))

print("找到 %d 条" % len(plan))
for h, off, vals in plan:
    txt = TXT[h]
    if len(txt) > len(vals):
        txt = txt[:len(vals)]
    slots = [ord(ch) for ch in txt] + [0x20] * (len(vals) - len(txt))
    for j, s in enumerate(slots):
        bp = off + 8 + j * 2
        d[bp] = (s >> 8) & 0xFF
        d[bp + 1] = s & 0xFF
    print("  hash 0x%08X @%-9d %d 槽位 -> %r" % (h, off, len(vals), txt))

assert len(d) == ent["size"]
raw[pos:pos + len(d)] = d
out = os.path.join(OUTDIR, "patch_probe_both_ascii.vpp_pc")
open(out, "wb").write(bytes(raw))
print()
print("已写出: %s (%d 字节)" % (out, len(raw)))

v2 = Vpp(out)
d2 = bytes(v2.read(v2.find("static_CH", "le_strings")))
print()
print("=== 复核 ===")
for h, off, vals in plan:
    u, _ = read_units(d2, off + 8)
    t = "".join(chr(x) for x, _ in u)
    print("  hash 0x%08X -> %r" % (h, t))
print()
print("  MD5: %s" % __import__("hashlib").md5(open(out, "rb").read()).hexdigest().upper())
