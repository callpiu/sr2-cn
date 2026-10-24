"""修复候选 A2：移除 static_CH 里全部 13 处 <img ...> 标记（原地等长替换）。

为什么测这个
    已确认：官方 patch.vpp_pc（无 static_CH）不崩；汉化 patch.vpp_pc（有 static_CH）必崩。
    → 崩溃由 static_CH 里的中文文本触发
    而崩溃时的字符串含 <img map_mp_bor_chopshop> 标记
    → 假设：游戏解析 <img> 标记时去查纹理资源，拿到已释放的指针

    本测试把 static_CH 里【全部 13 处 <img ...>】替换成等长占位文字。
    - 如果不崩 → 锁定 <img> 标记解析路径
    - 如果仍崩 → 与 <img> 无关，是中文文本本身

做法
    原地修改，槽位数完全不变 → le_strings 条目大小不变 → VPP 结构不变
    替换文字用【字表里存在的 ASCII 字符】，避免渲染异常
"""
import os, sys, struct, hashlib, re

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(G, "patch.vpp_pc")
OUTDIR = r"F:\sr2-cn\_fix_candidates"
OUT = os.path.join(OUTDIR, "patch_fixA2_noimg.vpp_pc")
os.makedirs(OUTDIR, exist_ok=True)

raw = bytearray(open(SRC, "rb").read())
v = Vpp(SRC)
ent = v.find("static_CH", "le_strings")
body = bytes(v.read(ent))
pos = raw.find(body)
if pos < 0:
    raise SystemExit("无法定位 static_CH body")

# 字表
CPS = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(CPS)}

d = bytearray(body)
b, c, off_at, offs = file_offsets(bytes(d))

# 找出所有含 <img ...> 的记录
TAG_RE = re.compile(r"<img [^>]*>")
jobs = []
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d) - 10):
        continue
    u, end = read_units(bytes(d), off + 8)
    if u is None:
        continue
    vals = [x for x, _ in u]
    t = "".join(S.get(x, "\uFFFD") for x in vals)
    for m in TAG_RE.finditer(t):
        tag = m.group(0)
        # 该标记对应的槽位：全 ASCII，槽位值 == 码点
        tag_slots = [ord(ch) for ch in tag]
        idx = -1
        for k in range(len(vals) - len(tag_slots) + 1):
            if vals[k:k + len(tag_slots)] == tag_slots:
                idx = k
                break
        if idx < 0:
            print("  [跳过] @%d 标记 %r 槽位未匹配" % (off, tag))
            continue
        jobs.append((off, idx, tag, len(vals)))

print("找到 %d 处 <img> 标记：" % len(jobs))
for off, idx, tag, ln in jobs:
    print("  @%-9d 位置 %-4d len=%-4d %r" % (off, idx, ln, tag))
print()

# 逐个替换：用 '.' 填充，保证是字表内的 ASCII
for off, idx, tag, ln in jobs:
    repl = "." * len(tag)
    for j, ch in enumerate(repl):
        struct.pack_into("<H", d, off + 8 + (idx + j) * 2, ord(ch))

assert len(d) == ent["size"]
raw[pos:pos + len(d)] = d
open(OUT, "wb").write(bytes(raw))
print("已写出: %s (%d 字节)" % (OUT, len(raw)))

# ---- 严格复核 ----
print()
print("=== 复核 ===")
v2 = Vpp(OUT)
e2 = v2.find("static_CH", "le_strings")
assert e2["size"] == ent["size"], "条目大小变了！"
d2 = bytes(v2.read(e2))
CPS2 = [int(l) for l in v2.read(v2.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S2 = {i + 0x20: chr(cp) for i, cp in enumerate(CPS2)}
b2, c2, oa2, offs2 = file_offsets(d2)

# 1) 所有原本含 img 的记录现在应该没有 img 了
still = 0
for off in dict.fromkeys(offs2):
    if not (0 < off <= len(d2) - 10):
        continue
    u, _ = read_units(d2, off + 8)
    if u is None:
        continue
    t = "".join(S2.get(x, "\uFFFD") for x, _ in u)
    if "<img" in t:
        still += 1
print("  剩余含 <img 的记录: %d 条（应为 0）" % still)

# 2) 打印修改过的记录
print()
print("  被修改的记录：")
for off, idx, tag, ln in jobs:
    u, _ = read_units(d2, off + 8)
    t = "".join(S2.get(x, "\uFFFD") for x, _ in u)
    bad = t.count("\uFFFD")
    print("    @%-9d 长度 %d  异常字符 %d" % (off, len(t), bad))
    print("      %s" % t[:100])

# 3) 逐字节比对：只有被替换的位置应该不同
diff = sum(1 for x, y in zip(body, d2) if x != y)
expect = sum(len(tag) * 2 for _, _, tag, _ in jobs)
print()
print("  字节差异: %d（预期 %d = %d 处标记 × 长度 × 2）" % (diff, expect, len(jobs)))
assert diff == expect, "差异字节数不符！"
print()
print("  ✓ 复核通过：只改了 %d 处 <img> 标记，其余完全不变" % len(jobs))
print("  ✓ 输出: %s" % OUT)
print("  ✓ MD5: %s" % hashlib.md5(open(OUT, "rb").read()).hexdigest().upper())
