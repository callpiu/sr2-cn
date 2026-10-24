# -*- coding: utf-8 -*-
# 决定性假设（重做）：g = B 按「繁体对应字的 Big5 编码」排序
# 之前 trad_map 不完整导致 0/9；这次用 opencc 全量转换
import sys, struct, bisect
sys.path.insert(0, r"F:/sr2-cn")
sys.path.insert(0, r"F:/sr2-cn/pylibs")
from opencc import OpenCC
from sr2font import Font

cc = OpenCC("s2t")
f = Font(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
B = [chr(c) for c in f.charlist]
CON = {"你": 371, "的": 1836, "兄": 422, "弟": 1035, "需": 2667,
       "要": 2296, "保": 391, "们": 362, "护": 2342}

# 繁简对照
trad = {c: cc.convert(c) for c in B}
print("样例:", {c: trad[c] for c in "们护你兄弟需要保位该"})


def key(c):
    t = trad[c]
    try:
        return (0, t.encode("big5"))
    except Exception:
        return (1, c.encode("utf-16-be"))


srt = sorted(B, key=key)
keys = [key(c) for c in srt]
print("\n=== g = B 按繁体 Big5 排序 ===")
hit = 0
for c, e in CON.items():
    exact = srt.index(c)
    pos = bisect.bisect_left(keys, key(c))
    ok = (srt[e] == c) or (pos == e)
    if ok:
        hit += 1
    print("  %-4s 引擎格=%-5d 精确名次=%-5d 二分插入点=%-5d %s" % (
        c, e, exact, pos, "✓" if ok else ""))
print("命中 %d/%d" % (hit, len(CON)))

# 若 们/护 吻合，输出它们的 Big5 名次
print("\n=== 们/护 的 Big5 名次 ===")
for c in "们护位该":
    print("  %s -> 繁体 %s  Big5名次=%d" % (c, trad[c], srt.index(c)))
