"""修复候选 A4：移除 static_CH 里全部 <img ...> 标记（原地等长替换）。

★ 关键修正：le_strings 的槽位是【大端 16 位】
    '的' = slot 1868 = 0x074C  →  字节 07 4C
    之前我用小端写成了 4C 07，把数据写坏了。

做法
    1. 用 read_units 解析每条记录（得到槽位值与字节位置）
    2. 定位 <img ...> 标记对应的槽位区间（标记全 ASCII，槽位值 == 码点）
    3. 把这些字节位置原地改写成 '.' (0x2E) 的大端表示 = 00 2E
    4. 复核：重新 read_units，槽位必须等于预期
"""
import os, sys, struct, hashlib, re

sys.path.insert(0, r"F:\sr2-cn\pylibs")
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SRC = os.path.join(G, "patch.vpp_pc")
OUTDIR = r"F:\sr2-cn\_fix_candidates"
OUT = os.path.join(OUTDIR, "patch_fixA4_noimg.vpp_pc")
os.makedirs(OUTDIR, exist_ok=True)

raw = bytearray(open(SRC, "rb").read())
v = Vpp(SRC)
ent = v.find("static_CH", "le_strings")
body = bytes(v.read(ent))
# 定位：用 find 但校验唯一性
pos = raw.find(body)
if pos < 0:
    raise SystemExit("无法定位 static_CH body")
pos2 = raw.find(body, pos + 1)
print("static_CH body 位置: 0x%X  重复出现: %s" % (pos, ("0x%X" % pos2) if pos2 >= 0 else "无"))

CPS = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(CPS)}

d = bytearray(body)
b, c, off_at, offs = file_offsets(bytes(d))

TAG_RE = re.compile(r"<img [^>]*>")
edits = []     # (记录off, 字节位置列表)
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
    byte_positions = []
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
            byte_positions.append(u[idx + j][1])       # 该槽位的字节位置
    if byte_positions:
        edits.append((off, byte_positions))

print("将修改 %d 条记录，共 %d 个槽位" % (len(edits), sum(len(e[1]) for e in edits)))
print()

# 原地改写为 '.' = 0x2E 的大端表示
for off, poss in edits:
    for bp in poss:
        d[bp] = 0x00
        d[bp + 1] = 0x2E

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

allok = True
for off, poss in edits:
    u, _ = read_units(d2, off + 8)
    got = [x for x, _ in u]
    t = "".join(S2.get(x, "\uFFFD") for x in got)
    bad = t.count("\uFFFD")
    has_img = "<img" in t
    if bad or has_img:
        allok = False
    print("  @%-9d 长度 %-4d 异常 %-3d img=%s" % (off, len(got), bad, has_img))
    print("      %s" % t[:95])

b2, c2, oa2, offs2 = file_offsets(d2)
still = 0
for off in dict.fromkeys(offs2):
    if not (0 < off <= len(d2) - 10):
        continue
    u, _ = read_units(d2, off + 8)
    if u is None:
        continue
    if "<img" in "".join(S2.get(x, "\uFFFD") for x, _ in u):
        still += 1

diff = sum(1 for x, y in zip(body, d2) if x != y)
expect = sum(len(e[1]) * 2 for e in edits)
print()
print("  剩余含 <img 的记录: %d（应为 0）" % still)
print("  字节差异: %d（预期 %d）" % (diff, expect))
print("  全部合法: %s" % ("是" if allok else "否"))
print()
if still == 0 and diff == expect and allok:
    print("  ✓✓ 修复成功且校验通过")
    print("  ✓ 输出: %s" % OUT)
    print("  ✓ MD5: %s" % hashlib.md5(open(OUT, "rb").read()).hexdigest().upper())
else:
    print("  ★ 复核未通过")
