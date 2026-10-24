# -*- coding: utf-8 -*-
# 放宽条件：搜所有含「们」且第5、16位是「们」的文本（不限字数、不限纯汉字）
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


print("=== 全部文本中第5、16位是「们」的记录 ===")
hits = []
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
        if len(t) < 16:
            continue
        if t[4] == "们" and t[15] == "们":
            hits.append((name, a, b_, t))
for name, a, b_, t in hits:
    print("  %s [%04X.%04X] (len=%d)\n     %s" % (name, a, b_, len(t), t[:80]))
print("共", len(hits), "条")

# 若仍无：改按「们」总数==2 且文本含直升机/突击语义
print("\n=== 含「们」×2 且含 直升/突击/停靠/面包 的记录 ===")
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
        if t.count("们") == 2 and any(k in t for k in ("直升", "突击", "停靠", "面包", "耐久")):
            print("  %s [%04X.%04X] %s" % (name, a, b_, t[:80]))

# 最后：22字记录全部列出（含直升机语义）
print("\n=== 22字且含 直升/机/突击 的记录 ===")
n = 0
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
        if any(k in t for k in ("直升", "机", "突击", "飞行", "降落")):
            print("  %s [%04X.%04X] %s" % (name, a, b_, t[:80]))
            n += 1
            if n >= 12:
                break
