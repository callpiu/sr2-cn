# -*- coding: utf-8 -*-
"""GC2: 检验假设 —— 引擎用的字符表(2838官方) 与 图集(2795汉化) 不一致。

已知(截图实测, 高置信度):
  正确字符 -> 屏幕上实际渲染出的字形
"""
import sys, os
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load(p, name, ext):
    v = Vpp(p); e = v.find(name, ext)
    t = v.read(e).decode("utf-8", "replace").replace("\r", "\n").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

Mh = load(os.path.join(G, "patch.vpp_pc"), "charlist_CH", "txt")          # 汉化 2795
Mo = load(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "charlist_CH", "txt")  # 官方 2838
print("汉化 charlist:", len(Mh), " 官方 charlist:", len(Mo))

pairs = [("你", "任"), ("的", "璨"), ("弟", "偶"), ("兄", "巧"), ("们", "位"),
         ("需", "雄"), ("要", "衡"), ("保", "伪"), ("护", "该")]

print("\n--- 假设A: 引擎字符表=官方(2838), 图集=汉化(2795) ---")
print("  期望 Mo[Mh.index(正确字)] == 屏幕上渲染的字")
okA = 0
for good, shown in pairs:
    i = Mh.index(ord(good))
    got = chr(Mo[i]) if i < len(Mo) else "?"
    hit = (got == shown)
    okA += hit
    print("   %s(汉化idx %4d) -> 官方表给出 %s   期望 %s   %s" % (good, i, got, shown, "OK" if hit else "x"))
print("   命中 %d/%d" % (okA, len(pairs)))

print("\n--- 假设B: 引擎字符表=汉化(2795), 图集=官方(2838) ---")
print("  期望 Mo[Mh.index(正确字)] == 屏幕上渲染的字 的另一种读法")
okB = 0
for good, shown in pairs:
    i = Mh.index(ord(good))
    got = chr(Mo[i]) if i < len(Mo) else "?"
    hit = (got == good)
    okB += hit
print("   (同上, 略)")

print("\n--- 假设C: 汉化表是否只是官方表的子序列(删43项) ---")
it = iter(Mo)
sub = all(any(x == y for y in it) for x in Mh)
print("   子序列:", sub)
removed = [c for c in Mo if c not in set(Mh)]
added = [c for c in Mh if c not in set(Mo)]
print("   官方有而汉化没有:", len(removed), "".join(chr(c) for c in removed[:60]))
print("   汉化有而官方没有:", len(added), "".join(chr(c) for c in added[:60]))

print("\n--- 假设D: 汉化表是否官方表重排(集合相同) ---")
print("   集合相同:", set(Mo) == set(Mh))
print("   升序(官方):", Mo == sorted(Mo), "  升序(汉化):", Mh == sorted(Mh))

print("\n--- 假设E: 引擎按 Unicode 升序排序后索引, 图集按文件顺序 ---")
srt = sorted(Mh)
okE = 0
for good, shown in pairs:
    i = Mh.index(ord(good))
    got = chr(srt[i])
    hit = (got == shown)
    okE += hit
    print("   %s(文件idx %4d) -> 排序表给出 %s  期望 %s  %s" % (good, i, got, shown, "OK" if hit else "x"))
print("   命中 %d/%d" % (okE, len(pairs)))
