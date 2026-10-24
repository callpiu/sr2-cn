# -*- coding: utf-8 -*-
"""核心验证：补丁表 vs 官方表的**字符集合差异**。
重点：目标字幕用到的字，在补丁表里是否都存在。
"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"F:/sr2-cn")
from minivpp import MiniVpp

v = MiniVpp(r"F:/sr2-cn/_v534_build.vpp_pc")
patch_raw = v.read(v.find("charlist_CH", "txt"))
patch = [int(x) for x in patch_raw.decode("ascii", "ignore").split() if x.strip().isdigit()]

v2 = MiniVpp(r"F:/sr2-cn/pristine/patch.vpp_pc")
orig_raw = v2.read(v2.find("charlist_CH", "txt"))
m = re.search(rb"(?m)^32\r?$", orig_raw)
orig = [int(x) for x in orig_raw[m.start():].decode("ascii", "ignore").split() if x.strip().isdigit()]

print("补丁表 %d 项  官方表 %d 项  差 %d" % (len(patch), len(orig), len(orig) - len(patch)))

sp = set(patch); so = set(orig)
only_orig = sorted(so - sp)
only_patch = sorted(sp - so)
print("\n仅官方表有 (%d 个):" % len(only_orig))
print("  ", "".join(chr(c) for c in only_orig[:80] if c < 0x10000))
print("\n仅补丁表有 (%d 个):" % len(only_patch))
print("  ", "".join(chr(c) for c in only_patch[:80] if c < 0x10000))

# 目标字幕用的字
target = "你的弟兄们需要保护赶到他们的目的地"
print("\n=== 目标字幕字串 '%s' ===" % target)
print("补丁表索引:", [patch.index(ord(c)) if ord(c) in sp else "缺失" for c in target])
print("官方表索引:", [orig.index(ord(c)) if ord(c) in so else "缺失" for c in target])

# 关键：哪些字补丁表没有
missing = [c for c in target if ord(c) not in sp]
print("\n★ 补丁表缺失的字:", "".join(missing) if missing else "(无)")

# 官方表里 0x4E00..0x9FFF 的汉字数量对比
def cjk(t):
    return [c for c in t if 0x4E00 <= c <= 0x9FFF]
print("\n补丁表汉字 %d 个，官方表汉字 %d 个" % (len(cjk(patch)), len(cjk(orig))))

# 检查是否"官方表 = 补丁表 + 一些额外字"（即补丁是官方表的子集）
print("\n补丁表 ⊂ 官方表 ?", sp.issubset(so))
print("官方表 ⊂ 补丁表 ?", so.issubset(sp))

# 索引对齐分析：找出两表前多少个相同
n = 0
for a, b in zip(patch, orig):
    if a == b:
        n += 1
    else:
        break
print("\n两表前 %d 项完全相同，第 %d 项起不同: 补丁=%d(0x%X) 官方=%d(0x%X)" % (
    n, n, patch[n], patch[n], orig[n], orig[n]))
print("  补丁[%d:%d] = %s" % (n, n + 12, patch[n:n + 12]))
print("  官方[%d:%d] = %s" % (n, n + 12, orig[n:n + 12]))
