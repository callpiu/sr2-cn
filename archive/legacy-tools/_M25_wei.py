# -*- coding: utf-8 -*-
# 统计「位」的全部出现语境，确定替换方案
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

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


from collections import Counter
ctx = Counter()
recs_with_wei = []
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
        n = t.count("位")
        if not n:
            continue
        recs_with_wei.append((name, a, b_, t, n))
        # 取每个「位」的前后字
        for j, ch in enumerate(t):
            if ch == "位":
                prev = t[j - 1] if j > 0 else "^"
                nxt = t[j + 1] if j + 1 < len(t) else "$"
                ctx[(prev, nxt)] += 1

print("含「位」的记录数 =", len(recs_with_wei), " 总出现 =", sum(r[4] for r in recs_with_wei))
print("\n=== 「位」的上下文（前字+后字）Top 25 ===")
for (pv, nx), c in ctx.most_common(25):
    print("  %s位%s : %d 次" % (pv, nx, c))

print("\n=== 含「位」的全部记录（voice_script，走字幕路径，最需要处理）===")
for name, a, b_, t, n in recs_with_wei:
    if name == "voice_script_CH":
        print("  [%04X.%04X] %s" % (a, b_, t[:64]))
