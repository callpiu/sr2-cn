# -*- coding: utf-8 -*-
# 决定性：比较 [10AF.1E62] 在 static_CH 与 voice_script_CH 里的槽位是否一致
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
cn = Vpp(CN)
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}

TARGET = (0x10AF, 0x1E62)


def load(name):
    d = cn.read(cn.find(name, "le_strings"))
    buckets, = struct.unpack_from("<H", d, 6)
    count, = struct.unpack_from("<I", d, 8)
    ptrs = struct.unpack_from("<%dI" % count, d, 12 + buckets * 8)
    return d, count, ptrs


for name in ("static_CH", "voice_script_CH", "platform_pc_CH"):
    d, count, ptrs = load(name)
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d):
            continue
        a, b_ = struct.unpack_from("<HH", d, p)
        if (a, b_) != TARGET:
            continue
        q = p + 4
        sl = []
        while True:
            s, = struct.unpack_from(">H", d, q)
            q += 2
            if s == 0:
                break
            sl.append(s)
        txt = "".join(B[s - 32] if 0 <= s - 32 < len(B) else "{%d}" % s for s in sl)
        print("=== %s [10AF.1E62] 槽位 %d 个 ===" % (name, len(sl)))
        print("  解码: %s" % txt)
        print("  槽位流: %s" % sl)
        # 逐位核对：槽位是否 = B.index(字)+32
        bad = [(j + 1, c, s, bidx[c] + 32) for j, (c, s) in enumerate(zip(txt, sl))
               if c in bidx and s != bidx[c] + 32]
        print("  槽位与 B.index+32 不一致的位数: %d" % len(bad))
        for j, c, s, exp in bad[:10]:
            print("    位%d '%s' 槽位=%d 应为=%d 差%+d" % (j, c, s, exp, s - exp))
        break
