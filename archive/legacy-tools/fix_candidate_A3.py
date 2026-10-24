"""修复候选 A3：移除 static_CH 里全部 <img ...> 标记（原地等长替换）。

★ 修正了 A2 的偏移 Bug：
    A2 写的是 off+8 + (idx+j)*2，但 off 已经是【槽位索引】而非字节偏移，
    所以实际写到了 off+8 + (idx+j)*4，把数据写坏了。
    正确写法：struct.pack_into("<H", d, (off + 8) + (idx + j) * 2, slot)

做法
    1. 解析每条记录为【槽位序列】
    2. 找到 <img ...> 的槽位位置（标记全 ASCII，槽位值 == 码点）
    3. 用 '.' 填充同样数量的位置
    4. 整条槽位序列写回（从 off+8 开始，每条 2 字节）
    5. 严格复核：读回来必须等于写进去的
"""
import os, sys, struct, hashlib, re

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(G, "patch.vpp_pc")
OUTDIR = r"F:\sr2-cn\_fix_candidates"
OUT = os.path.join(OUTDIR, "patch_fixA3_noimg.vpp_pc")
os.makedirs(OUTDIR, exist_ok=True)

raw = bytearray(open(SRC, "rb").read())
v = Vpp(SRC)
ent = v.find("static_CH", "le_strings")
body = bytes(v.read(ent))
pos = raw.find(body)
if pos < 0:
    raise SystemExit("无法定位 static_CH body")

CPS = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(CPS)}

d = bytearray(body)
b, c, off_at, offs = file_offsets(bytes(d))

TAG_RE = re.compile(r"<img [^>]*>")
plan = []      # (off, 新槽位序列)
for off in dict.fromkeys(offs):
    if not (0 < off <= len(d) - 10):
        continue
    u, end = read_units(bytes(d), off + 8)
    if u is None:
        continue
    vals = [x for x, _ in u]
    t = "".join(S.get(x, "\uFFFD") for x in vals)
    if "<img" not in t:
        continue
    new = list(vals)
    cnt = 0
    for m in TAG_RE.finditer(t):
        tag = m.group(0)
        tag_slots = [ord(ch) for ch in tag]
        idx = -1
        for k in range(len(vals) - len(tag_slots) + 1):
            if vals[k:k + len(tag_slots)] == tag_slots:
                idx = k
                break
        if idx < 0:
            print("  [跳过] @%d %r 槽位未匹配" % (off, tag))
            continue
        for j in range(len(tag)):
            new[idx + j] = ord('.')
        cnt += 1
    if cnt:
        plan.append((off, new, len(vals)))

print("计划修改 %d 条记录：" % len(plan))
for off, new, ln in plan:
    print("  @%-9d 长度 %d" % (off, ln))
print()

# ---- 写回：整条槽位序列 ----
for off, new, ln in plan:
    assert len(new) == ln
    for j, s in enumerate(new):
        struct.pack_into("<H", d, (off + 8) + j * 2, s)

assert len(d) == ent["size"], (len(d), ent["size"])
raw[pos:pos + len(d)] = d
open(OUT, "wb").write(bytes(raw))
print("已写出: %s (%d 字节)" % (OUT, len(raw)))

# ---- 复核 ----
print()
print("=== 复核 ===")
v2 = Vpp(OUT)
e2 = v2.find("static_CH", "le_strings")
assert e2["size"] == ent["size"]
d2 = bytes(v2.read(e2))
CPS2 = [int(l) for l in v2.read(v2.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S2 = {i + 0x20: chr(cp) for i, cp in enumerate(CPS2)}

ok = True
for off, new, ln in plan:
    u, _ = read_units(d2, off + 8)
    got = [x for x, _ in u]
    if got != new:
        print("  ★ @%d 读回不一致！" % off)
        ok = False
        continue
    t = "".join(S2.get(x, "\uFFFD") for x in got)
    print("  @%-9d 长度 %d  异常 %d" % (off, len(got), t.count("\uFFFD")))
    print("      %s" % t[:95])
    assert "<img" not in t

# 全文件 img 计数
still = 0
b2, c2, oa2, offs2 = file_offsets(d2)
for off in dict.fromkeys(offs2):
    if not (0 < off <= len(d2) - 10):
        continue
    u, _ = read_units(d2, off + 8)
    if u is None:
        continue
    if "<img" in "".join(S2.get(x, "\uFFFD") for x, _ in u):
        still += 1

# 字节差异
diff = sum(1 for x, y in zip(body, d2) if x != y)
expect = sum((len(new) - sum(1 for a, bb in zip(new, [x for x, _ in read_units(body, off + 8)[0]]) if a != bb)) * 2 for off, new, ln in plan)
print()
print("  剩余含 <img 的记录: %d（应为 0）" % still)
print("  逐条读回一致: %s" % ("是" if ok else "否"))
print("  字节差异: %d" % diff)
print()
if still == 0 and ok:
    print("  ✓ 修复成功")
    print("  ✓ 输出: %s" % OUT)
    print("  ✓ MD5: %s" % hashlib.md5(open(OUT, "rb").read()).hexdigest().upper())
else:
    print("  ★ 复核未通过")
