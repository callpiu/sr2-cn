# -*- coding: utf-8 -*-
# 最后排查：含 2 个「们」且与直升机/飞行相关的文本 + Carlos 台词块
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
cn = Vpp(CN)
f = Font(CN)
B = [chr(c) for c in f.charlist]

DISP = "任璨偶巧们校衡勾远藐乱携伪该亡们通像匪冰挺拮"


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


print("=== 含 2 个「们」的直升机/飞行相关文本 ===")
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
        if t.count("们") == 2 and any(k in t for k in ("直升", "飞行", "降落", "起飞", "空中", "抓")):
            print("  %s [%04X.%04X] 们位置=%s\n     %s" % (
                name, a, b_, [j + 1 for j, c in enumerate(t) if c == "们"], t[:80]))

# 关键：把显示句按「正常字 E=B序-5」重新解释
# 若某显示字 d 满足「B.index(d)-5 是某字的正常 E」，则该字正常
# 我们已知们正常。检查其余 21 字的 B 索引-5 是否落在「合理」范围
print("\n=== 显示句各字的 B 索引与 E ===")
for i, d in enumerate(DISP, 1):
    k = B.index(d) if d in B else -1
    print("  %2d %s B序=%-5d E=%-5d %s" % (i, d, k, k - 5, "★们(正常)" if d == "们" else ""))
