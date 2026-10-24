# -*- coding: utf-8 -*-
# 用 voice_script_CH 的物理存储顺序（按任务分组）定位 8848.0138 附近的完整任务对白块
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
cn = Vpp(CN)
f = Font(CN)
B = [chr(c) for c in f.charlist]

d = cn.read(cn.find("voice_script_CH", "le_strings"))
buckets, = struct.unpack_from("<H", d, 6)
count, = struct.unpack_from("<I", d, 8)
ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)


def rec(p):
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


tpos = None
for i in range(count):
    if ptrs[i] + 6 <= len(d) and struct.unpack_from("<HH", d, ptrs[i]) == (0x8848, 0x0138):
        tpos = i
        break
print("8848.0138 在 voice_script_CH 的 index =", tpos, "/", count)

print("\n=== 物理邻居（index %s±25）===" % tpos)
for j in range(max(0, tpos - 25), min(count, tpos + 26)):
    try:
        a, b_, t = rec(ptrs[j])
    except Exception:
        continue
    mark = " ★" if (a, b_) == (0x8848, 0x0138) else ""
    print("  [%5d] [%04X.%04X]%s %s" % (j, a, b_, mark, t[:66]))
