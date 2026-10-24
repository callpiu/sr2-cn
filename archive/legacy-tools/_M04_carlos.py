# -*- coding: utf-8 -*-
# 确认 0x88xx id 段 = 卡洛斯对白；列出该段全部记录定位这句的语境
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
cn = Vpp(CN)
f = Font(CN)
B = [chr(c) for c in f.charlist]

for name in ("voice_script_CH", "static_CH"):
    d = cn.read(cn.find(name, "le_strings"))
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    rows = []
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d):
            continue
        id1, id2 = struct.unpack_from("<HH", d, p)
        if not (0x8820 <= id1 <= 0x88A0):
            continue
        q = p + 4
        out = []
        while True:
            s, = struct.unpack_from(">H", d, q)
            q += 2
            if s == 0:
                break
            k = s - 32
            out.append(B[k] if 0 <= k < len(B) else "{%d}" % s)
        rows.append((id1, id2, "".join(out)))
    rows.sort()
    print("\n=== %s 中 id1 ∈ [0x8820,0x88A0] 的记录（%d 条）===" % (name, len(rows)))
    for a, b_, t in rows:
        mark = " ★" if (a, b_) == (0x8858, 0x6942) else ""
        print("  [%04X.%04X]%s %s" % (a, b_, mark, t[:72]))
