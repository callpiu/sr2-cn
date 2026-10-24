# -*- coding: utf-8 -*-
"""GG3: 从两张截图读出「槽位 -> 实际渲染格子」映射, 反解变换。"""
import sys, os
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pv = Vpp(os.path.join(G, "patch.vpp_pc"))
T = [int(s) for s in pv.read(pv.find("charlist_CH", "txt")).decode("utf-8", "replace").replace("\r", "\n").split("\n") if s.strip().isdigit()]
pos = {}
for i, c in enumerate(T):
    pos.setdefault(c, i)

# (槽位, 期望字, 截图实渲染字)
OBS = [
    (403, "你", "任"), (1868, "的", "璨"), (1067, "弟", "偶"), (454, "兄", "巧"),
    (364, "们", "位"), (2699, "需", "雄"), (2328, "要", "衡"), (423, "保", "伪"),
    (1222, "护", "该"),
    (510, "出", "衡"), (613, "去", "勾"), (2389, "谈", "远"), (502, "几", "藐"),
    (1995, "笔", "乱"), (1824, "生", "携"), (1159, "意", "空"), (2822, "，", "空"),
    (356, "他", "亡"), (460, "免", "通"), (2563, "遭", "像"), (2312, "袭", "匪"),
    (479, "击", "冰"),
]

print("%-6s %-4s %-4s %-8s %-8s %-6s %-8s" % ("槽位", "期望", "渲染", "期望idx", "渲染idx", "渲染cell", "Δcell"))
pairs = []
for slot, exp, got in OBS:
    ie = pos.get(ord(exp)); ig = pos.get(ord(got))
    if ig is None:
        print("%-6d %-4s %-4s %-8s %-8s  (渲染字不在字符表)" % (slot, exp, got, ie, ig)); continue
    cell = ig + 32
    pairs.append((slot, cell))
    print("%-6d %-4s %-4s %-8s %-8d %-8d %+d" % (slot, exp, got, ie, ig, cell, cell - slot))

print("\n--- 假设检验 ---")
sl = [s for s, c in pairs]
cl = [c for s, c in pairs]
d = [c - s for s, c in pairs]
print("Δ 序列:", d)
print("Δ 恒定? ", len(set(d)) == 1)

def test(name, fn):
    ok = sum(1 for s, c in pairs if fn(s) == c)
    print("  %-42s %d/%d %s" % (name, ok, len(pairs), "OK" if ok == len(pairs) else ""))

N = 2795
test("cell = slot",                lambda s: s)
test("cell = slot - 5",            lambda s: s - 5)
test("cell = slot + 5",            lambda s: s + 5)
test("cell = slot - 32",           lambda s: s - 32)
test("cell = slot + 32",           lambda s: s + 32)
test("cell = slot - 5 (mod N)",    lambda s: (s - 5) % N)
# 列/行变换：col = s%65, row = s//65
for dc in (-5, 5, -1, 1):
    test("col+=%d (65列)" % dc, lambda s, dc=dc: (s % 65 + dc) % 65 + (s // 65) * 65)
for dr in (-1, 1, -5, 5):
    test("row+=%d (65列)" % dr, lambda s, dr=dr: (s % 65) + ((s // 65 + dr) % 43) * 65)
# 60 列网格
for dc in (-5, 5, 0):
    test("60列 col+=%d" % dc, lambda s, dc=dc: (s % 60 + dc) % 60 + (s // 60) * 60)
test("60列 无偏移", lambda s: (s % 60) + (s // 60) * 60)
test("cell = (s-5) 的 60 列重排", lambda s: ((s - 5) % 60) + ((s - 5) // 60) * 65)
