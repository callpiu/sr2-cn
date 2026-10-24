# -*- coding: utf-8 -*-
# v530：武器店分类「已扔出」→「投掷类」（2 条，英文 Thrown）
import sys, os, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
P = os.path.join(GAME, "patch.vpp_pc")
V529 = "92de2f2e6916a382823f0edab284f725"

cur = hashlib.md5(open(P, 'rb').read()).hexdigest()
print("当前 patch:", cur, "(v529?", cur == V529, ")")
assert cur == V529, "基线不是 v529，中止"

v = Vpp(P)
cl = [int(s) for s in v.read(v.find("charlist_CH", "txt")).decode('utf-8').split('\n') if s.strip().isdigit()]
c2s = {}
for i, cp in enumerate(cl):
    if cp >= 0x100:
        c2s.setdefault(chr(cp), i + 0x20)

OLD, NEW = '已扔出', '投掷类'
assert len(OLD) == len(NEW) == 3, "长度不等"
for ch in NEW:  # ★逐字查（c2s 键是单字符）
    assert ch in c2s, "字表缺字 %r" % ch

old_slots = b''.join(int(c2s[ch]).to_bytes(2, 'big') for ch in OLD)
new_slots = b''.join(int(c2s[ch]).to_bytes(2, 'big') for ch in NEW)
print("槽值:", {ch: c2s[ch] for ch in set(OLD + NEW)})
print("旧槽字节:", old_slots.hex(), "-> 新:", new_slots.hex())

data = bytearray(open(P, 'rb').read())

# 字节级搜索，前置断言：后随 0x0000 终止符
pos = []
i = 0
while True:
    j = data.find(old_slots, i)
    if j < 0:
        break
    if data[j+6:j+8] == b'\x00\x00':
        rid = (int.from_bytes(data[j-4:j-2], 'little'),
               int.from_bytes(data[j-2:j], 'little'))
        pos.append((j, rid))
    i = j + 1

print("匹配(带终止符): %d 处" % len(pos))
for j, rid in pos:
    print("  @0x%-7X ID=%d,%d" % (j, rid[0], rid[1]))
assert len(pos) == 2, "应恰好 2 条，实际 %d" % len(pos)

for j, _ in pos:
    data[j:j+6] = new_slots

out = r"F:\sr2-cn\_fix_candidates\patch_v530.vpp_pc"
open(out, 'wb').write(bytes(data))
m = hashlib.md5(bytes(data)).hexdigest()
old_b = open(P, 'rb').read()
diff = sum(1 for a, b in zip(old_b, data) if a != b)
print("\n候选 v530: %s  %d bytes" % (m, os.path.getsize(out)))
print("相对 v529 差异字节: %d (预期 12 = 2条×3字×2字节)" % diff)
assert diff == 12, "差异字节数不符"
print("OK")
