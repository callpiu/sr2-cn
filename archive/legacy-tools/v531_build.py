# -*- coding: utf-8 -*-
# v531：任务完成界面「等待主机玩家」→「等候主机玩家」（1 条）
import sys, os, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
P = os.path.join(GAME, "patch.vpp_pc")
V530 = "ead5dcf22ac724db83c470ec128df6e2"

cur = hashlib.md5(open(P, 'rb').read()).hexdigest()
print("当前 patch:", cur, "(v530?", cur == V530, ")")
assert cur == V530, "基线不是 v530，中止"

v = Vpp(P)
cl = [int(s) for s in v.read(v.find("charlist_CH", "txt")).decode('utf-8').split('\n') if s.strip().isdigit()]
c2s = {}
for i, cp in enumerate(cl):
    if cp >= 0x100:
        c2s.setdefault(chr(cp), i + 0x20)

OLD, NEW = '等待主机玩家', '等候主机玩家'
assert len(OLD) == len(NEW) == 6, "长度不等"
for ch in NEW:  # 逐字查（c2s 键是单字符）
    assert ch in c2s, "字表缺字 %r" % ch

# 只有第 2 字不同：待 -> 候
old_slots = b''.join(int(c2s[ch]).to_bytes(2, 'big') for ch in OLD)
new_slots = b''.join(int(c2s[ch]).to_bytes(2, 'big') for ch in NEW)
print("槽值: 等=%d 待=%d 候=%d" % (c2s['等'], c2s['待'], c2s['候']))
print("旧槽字节:", old_slots.hex(), "-> 新:", new_slots.hex())

data = bytearray(open(P, 'rb').read())

pos = []
i = 0
while True:
    j = data.find(old_slots, i)
    if j < 0:
        break
    if data[j+12:j+14] == b'\x00\x00':
        rid = (int.from_bytes(data[j-4:j-2], 'little'),
               int.from_bytes(data[j-2:j], 'little'))
        pos.append((j, rid))
    i = j + 1

print("匹配(带终止符): %d 处" % len(pos))
for j, rid in pos:
    print("  @0x%-7X ID=%d,%d" % (j, rid[0], rid[1]))
assert len(pos) == 1, "应恰好 1 条，实际 %d" % len(pos)

j, _ = pos[0]
data[j:j+12] = new_slots

out = r"F:\sr2-cn\_fix_candidates\patch_v531.vpp_pc"
open(out, 'wb').write(bytes(data))
m = hashlib.md5(bytes(data)).hexdigest()
old_b = open(P, 'rb').read()
diff = sum(1 for a, b in zip(old_b, data) if a != b)
print("\n候选 v531: %s  %d bytes" % (m, os.path.getsize(out)))
print("相对 v530 差异字节: %d (预期 2)" % diff)
assert diff == 2, "差异字节数不符"
print("OK")
