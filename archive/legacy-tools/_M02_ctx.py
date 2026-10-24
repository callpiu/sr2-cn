# -*- coding: utf-8 -*-
# 1) dump 8858.6942 在 static_US 里的原始字节，搞清英文表记录格式
# 2) 看 static_CH 里该记录的「物理邻居」（pointer 顺序 = 常见同组提示）
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"


def parse_charlist(raw):
    B = []
    for L in raw.split(b"\r\n"):
        s = L.strip()
        if not s or s.startswith(b"//") or s.startswith(b"count="):
            continue
        for tok in s.split():
            if tok.isdigit():
                B.append(chr(int(tok)))
    return B


cn = Vpp(CN)
B = parse_charlist(cn.read(cn.find("charlist_CH", "txt")))

d_cn = cn.read(cn.find("static_CH", "le_strings"))
vv = Vpp(VANILLA)
d_us = vv.read(vv.find("static_US", "le_strings"))

# --- 1) dump static_US 中目标记录的原始字节
buckets_us, = struct.unpack_from("<H", d_us, 6)
count_us, = struct.unpack_from("<I", d_us, 8)
ptrs_us = struct.unpack_from("<%dI" % count_us, d_us, 12 + buckets_us * 8)
print("static_US count =", count_us)
for i in range(count_us):
    p = ptrs_us[i]
    if p + 6 > len(d_us):
        continue
    id1, id2 = struct.unpack_from("<HH", d_us, p)
    if (id1, id2) == (0x8858, 0x6942):
        print("\n★ 英文表 [8858.6942] 记录偏移 = 0x%X" % p)
        print("  原始 80 字节:")
        chunk = d_us[p:p + 80]
        print("   ", chunk.hex(" "))
        print("   ASCII:", "".join(chr(b) if 32 <= b < 127 else "." for b in chunk))
        break

# --- 2) static_CH 目标记录的物理位置与邻居
buckets_cn, = struct.unpack_from("<H", d_cn, 6)
count_cn, = struct.unpack_from("<I", d_cn, 8)
ptrs_cn = struct.unpack_from("<%dI" % count_cn, d_cn, 12 + buckets_cn * 8)
print("\nstatic_CH count =", count_cn)
tpos = None
for i in range(count_cn):
    if ptrs_cn[i] and struct.unpack_from("<HH", d_cn, ptrs_cn[i]) == (0x8858, 0x6942):
        tpos = i
        break
print("目标在 static_CH 的 index =", tpos)


def rec_cn(p):
    id1, id2 = struct.unpack_from("<HH", d_cn, p)
    q = p + 4
    out = []
    while True:
        s, = struct.unpack_from(">H", d_cn, q)
        q += 2
        if s == 0:
            break
        i = s - 32
        out.append(B[i] if 0 <= i < len(B) else "{%d}" % s)
    return id1, id2, "".join(out)


print("\n=== static_CH 中物理相邻的记录（index %s±12）===" % tpos)
for j in range(max(0, tpos - 12), min(count_cn, tpos + 13)):
    try:
        a, b_, t = rec_cn(ptrs_cn[j])
    except Exception:
        continue
    mark = " ★" if j == tpos else ""
    print("  [%5d] [%04X.%04X]%s %s" % (j, a, b_, mark, t[:70]))
