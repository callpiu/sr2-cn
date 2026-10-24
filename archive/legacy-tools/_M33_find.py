# -*- coding: utf-8 -*-
# 按「们」的位置反查：22字文本，第5位和第16位是「们」
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
cn = Vpp(CN)
f = Font(CN)
B = [chr(c) for c in f.charlist]

DISP = "任璨偶巧们校衡勾远藐乱携 伪该亡们通像匪冰挺拮".replace(" ", "")
print("显示句 =", DISP, " 长度 =", len(DISP))
print("「们」位置:", [i + 1 for i, c in enumerate(DISP) if c == "们"])


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


print("\n=== 22字且第5、16位是「们」的文本 ===")
for name in ("voice_script_CH", "static_CH"):
    d, count, ptrs = load(name)
    for i in range(count):
        p = ptrs[i]
        if p + 6 > len(d):
            continue
        try:
            a, b_, t = rec(d, p)
        except Exception:
            continue
        han = [c for c in t if 0x4E00 <= ord(c) <= 0x9FFF]
        if len(han) != 22:
            continue
        if han[4] != "们" or han[15] != "们":
            continue
        print("  %s [%04X.%04X]\n     %s" % (name, a, b_, t))
        # 逐字对照
        disp = DISP
        print("     逐字: 源 -> 显示")
        for j in range(min(len(han), len(disp))):
            print("       %2d %s -> %s %s" % (j + 1, han[j], disp[j],
                  "✓" if han[j] == disp[j] else ""))
