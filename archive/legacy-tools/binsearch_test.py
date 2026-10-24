# -*- coding: utf-8 -*-
"""核心假说：引擎对 common 图集顺序表（未按码点排序）做二分查找 → 落到错误索引。
用 9 个实证映射检验多种查找变体。"""
import json

J = json.load(open(r"F:\sr2-cn\_day_2026-10-07\04_规则与数据\_expected_charlist.json"))
N = len(J)

# 9 个实证映射: 输入字符 -> 屏幕实际显示的码点
OBS = [
    ("们", 0x4EEC, 0x4F4D),
    ("你", 0x4F60, 0x4EFB),
    ("保", 0x4FDD, 0x4F2A),
    ("兄", 0x5144, 0x5DE7),
    ("弟", 0x5F1F, 0x5076),
    ("护", 0x62A4, 0x8BE5),
    ("的", 0x7684, 0x74A8),
    ("要", 0x8981, 0x8861),
    ("需", 0x9700, 0x96C4),
]

def lower_bound(a, k):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < k: lo = mid + 1
        else: hi = mid
    return lo

def upper_bound(a, k):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= k: lo = mid + 1
        else: hi = mid
    return lo

def bs_lastmid(a, k):
    """常见引擎写法：lo=0 hi=n-1, 返回最后 mid"""
    lo, hi = 0, len(a) - 1
    res = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        res = mid
        if a[mid] == k: return mid
        elif a[mid] < k: lo = mid + 1
        else: hi = mid - 1
    return res

def bs_lastmid_le(a, k):
    """找不到时返回 lo-1 (最后一个 <=k)"""
    lo, hi = 0, len(a) - 1
    res = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] <= k:
            res = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return res

def lin_first_ge(a, k):
    for i, v in enumerate(a):
        if v >= k: return i
    return len(a)

def lin_first_le(a, k):
    r = -1
    for i, v in enumerate(a):
        if v <= k: r = i
    return r

def lin_exact(a, k):
    for i, v in enumerate(a):
        if v == k: return i
    return -1

VARIANTS = [
    ("lower_bound", lambda a,k: lower_bound(a,k)),
    ("upper_bound", lambda a,k: upper_bound(a,k)),
    ("bs_lastmid",  lambda a,k: bs_lastmid(a,k)),
    ("bs_lastmid_le", lambda a,k: bs_lastmid_le(a,k)),
    ("lin_first_ge", lambda a,k: lin_first_ge(a,k)),
    ("lin_first_le", lambda a,k: lin_first_le(a,k)),
    ("lin_exact",   lambda a,k: lin_exact(a,k)),
]

print(f"common 图集顺序表: {N} 项 (未排序)\n")
for name, fn in VARIANTS:
    hits = 0
    detail = []
    for ch, cp, out in OBS:
        i = fn(J, cp)
        if 0 <= i < N and J[i] == out:
            hits += 1
            detail.append(f"{ch}:OK")
        else:
            got = f"U+{J[i]:04X}" if 0 <= i < N else "越界"
            detail.append(f"{ch}:期望U+{out:04X}/实得{got}@{i}")
    print(f"[{name:14s}] 命中 {hits}/9   " + "  ".join(detail))

print("\n=== 输入码点在图集顺序表中的实际位置（线性精确查找）===")
for ch, cp, out in OBS:
    pos = [i for i, v in enumerate(J) if v == cp]
    opos = [i for i, v in enumerate(J) if v == out]
    print(f"  {ch} U+{cp:04X} 在表中位置 {pos}   ->  显示 U+{out:04X} 位置 {opos}")

print("\n=== 表的结构：降序点（排序中断处）===")
desc = [i for i in range(N-1) if J[i] > J[i+1]]
print(f"  共 {len(desc)} 个降序点，前 40 个: {desc[:40]}")
print(f"  后 10 个: {desc[-10:]}")
# 最长升序段
best = cur = 1; bs = 0; cs = 0
for i in range(1, N):
    if J[i] > J[i-1]:
        cur += 1
        if cur > best: best, bs = cur, cs
    else:
        cur = 1; cs = i
print(f"  最长严格升序段: 长度 {best}, 起始 {bs} (码点 U+{J[bs]:04X}..U+{J[bs+best-1]:04X})")
