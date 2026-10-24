"""修复候选：把两个活动串改成 ASCII（保底方案）。

背景
    已确认：static_CH 里的这两条数据【完全正确】（解码为「弟兄们需要你的保护」等），
    但活动 HUD 渲染成乱码。偏移不是常量（实测每个字要求的偏移都不同：
    -699 / +1362 / +78 / -1700 ...），说明 HUD 用的是【另一套字形索引空间】，
    静态无法推出映射。

保底方案
    ASCII 区在两种字体里都渲染正常（用户界面英文一直没问题）。
    把这两条串的中文部分换成 ASCII 文字，即可正常显示。

做法
    ★ 只改【长度不变】的内容：原地替换槽位，条目大小、VPP 结构完全不动。
    ★ 保留原字符串长度（用空格补齐）。
"""
import os, sys, struct, shutil

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(G, "patch.vpp_pc")
OUTDIR = r"F:\sr2-cn\_fix_candidates"
OUT = os.path.join(OUTDIR, "patch_fixB_ascii_activity.vpp_pc")
os.makedirs(OUTDIR, exist_ok=True)

H1, H2 = 0x84F287ED, 0x10AF1E62
# 目标文本（ASCII，长度 <= 原中文部分长度，空格补齐）
NEW = {
    H1: "Your homies need your protection",      # 32 字符（原 39 槽位）
    H2: "Protect your homies from attackers",    # 35 字符（原 50 槽位）
}

raw = bytearray(open(SRC, "rb").read())
v = Vpp(SRC)
ent = v.find("static_CH", "le_strings")
body = bytes(v.read(ent))
pos = raw.find(body)
if pos < 0:
    raise SystemExit("无法定位 static_CH")
print("static_CH: %d 字节, 文件偏移 0x%X" % (ent["size"], pos))

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
    vals = [x for x, _ in u]
    plan.append((h, off, vals))

print("找到 %d 条记录" % len(plan))
print()
for h, off, vals in plan:
    txt = NEW[h]
    if len(txt) > len(vals):
        raise SystemExit("新文本 %d 字符 > 原 %d 槽位，无法等长替换" % (len(txt), len(vals)))
    # 写入：ASCII 槽位 = 码点；剩余用空格 (0x20) 补齐
    new_slots = [ord(ch) for ch in txt] + [0x20] * (len(vals) - len(txt))
    # 大端写入
    for j, s in enumerate(new_slots):
        bp = off + 8 + j * 2
        d[bp] = (s >> 8) & 0xFF
        d[bp + 1] = s & 0xFF
    print("  hash 0x%08X @%-9d 原 %d 槽位 -> 新文本 %d 字符 + %d 空格" %
          (h, off, len(vals), len(txt), len(vals) - len(txt)))
    print("    %s" % txt)

assert len(d) == ent["size"], (len(d), ent["size"])
raw[pos:pos + len(d)] = d
open(OUT, "wb").write(bytes(raw))
print()
print("已写出: %s (%d 字节)" % (OUT, len(raw)))

# ---- 复核 ----
print()
print("=== 复核 ===")
v2 = Vpp(OUT)
e2 = v2.find("static_CH", "le_strings")
assert e2["size"] == ent["size"]
d2 = bytes(v2.read(e2))
for h, off, vals in plan:
    u, _ = read_units(d2, off + 8)
    got = [x for x, _ in u]
    t = "".join(chr(x) if 0x20 <= x < 0x7F else "?" for x in got)
    print("  hash 0x%08X -> %r" % (h, t))
    assert all(0x20 <= x < 0x7F for x in got), "仍有非 ASCII！"
print()
print("  ✓ 两条串已全部为 ASCII，长度不变")
print("  ✓ MD5: %s" % __import__("hashlib").md5(open(OUT, "rb").read()).hexdigest().upper())
