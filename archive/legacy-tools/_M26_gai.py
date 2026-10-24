# -*- coding: utf-8 -*-
# 「该」的上下文统计（评估替换代价，为修「护」做准备）
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp
from collections import Counter

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
cn = Vpp(CN)
f = Font(CN)
B = [chr(c) for c in f.charlist]


def load(name):
    d = cn.read(cn.find(name, "le_strings"))
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    return d, count, ptrs


def rec(d, p):
    id1, id2 = struct.unpack_from("<HH", d, p)
    q = p + 4
    out = []
    while True:
        s, = struct.unpack_from(">H", d, q)
        q += 2
        if s == 0:
            break
        k = s - 32
        out.append(B[k] if 0 <= k < len(B) else "{%d}" % s)
    return id1, id2, "".join(out)


ctx = Counter()
for name in ("voice_script_CH", "static_CH", "platform_pc_CH"):
    d, count, ptrs = load(name)
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d):
            continue
        try:
            a, b_, t = rec(d, p)
        except Exception:
            continue
        for j, ch in enumerate(t):
            if ch == "该":
                prev = t[j - 1] if j > 0 else "^"
                nxt = t[j + 1] if j + 1 < len(t) else "$"
                ctx[(prev, nxt)] += 1

print("=== 「该」的上下文 Top 25 ===")
for (pv, nx), c in ctx.most_common(25):
    print("  %s该%s : %d 次" % (pv, nx, c))

# 「护」的上下文
ctx2 = Counter()
for name in ("voice_script_CH", "static_CH", "platform_pc_CH"):
    d, count, ptrs = load(name)
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d):
            continue
        try:
            a, b_, t = rec(d, p)
        except Exception:
            continue
        for j, ch in enumerate(t):
            if ch == "护":
                prev = t[j - 1] if j > 0 else "^"
                nxt = t[j + 1] if j + 1 < len(t) else "$"
                ctx2[(prev, nxt)] += 1
print("\n=== 「护」的上下文 Top 15 ===")
for (pv, nx), c in ctx2.most_common(15):
    print("  %s护%s : %d 次" % (pv, nx, c))
