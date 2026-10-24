# -*- coding: utf-8 -*-
# 步骤3（决定性）：汉化版 static_CH 按「简体表 B」解码 -> 找出漏网繁体字
# 假设：汉化补丁把 static_CH 的槽位按 B 重编码，但漏了少数繁体字
#       -> 那些字槽位仍是按官方繁体表 T 编码的 -> 引擎按 B 解码 -> 乱码
import sys, os, struct, re
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
CN      = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"


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


vv, cn = Vpp(VANILLA), Vpp(CN)
T = parse_charlist(vv.read(vv.find("charlist_CH", "txt")))
B = parse_charlist(cn.read(cn.find("charlist_CH", "txt")))
BS, TS = set(B), set(T)

data = cn.read(cn.find("static_CH", "le_strings"))
ver, buckets = struct.unpack_from("<HH", data, 4)
count, = struct.unpack_from("<I", data, 8)
ptrs = struct.unpack_from("<%dI" % count, data, 12 + buckets * 8)
print("汉化版 static_CH: count=%d" % count)

# 官方版用于对照
vdata = vv.read(vv.find("static_CH", "le_strings"))
vcount, = struct.unpack_from("<I", vdata, 8)
vptrs = struct.unpack_from("<%dI" % vcount, vdata, 12 + buckets * 8)
print("官方版 static_CH: count=%d" % vcount)

def slots(d, p):
    """读一条记录的槽位流，返回 (id1, id2, [槽位...], end)"""
    id1, id2 = struct.unpack_from("<HH", d, p)
    q = p + 4
    out = []
    while True:
        s, = struct.unpack_from(">H", d, q)
        q += 2
        if s == 0:
            break
        out.append(s)
    return id1, id2, out, q


def to_text(sl, table):
    r = []
    for s in sl:
        i = s - 32
        r.append(table[i] if 0 <= i < len(table) else "{%d}" % s)
    return "".join(r)


# 1) 两版同一记录（按 id 对齐）的槽位是否相同
same = diff = 0
slot_mismatch = []
for i in range(min(count, vcount)):
    try:
        a = slots(data, ptrs[i]); b = slots(vdata, vptrs[i])
    except Exception:
        continue
    if a[0] == b[0] and a[1] == b[1]:
        if a[2] == b[2]:
            same += 1
        else:
            diff += 1
            if len(slot_mismatch) < 10:
                slot_mismatch.append((a[0], a[1], to_text(a[2], T), to_text(b[2], B)))
print("\n同 id 记录：槽位完全相同 %d 条，不同 %d 条" % (same, diff))
print("\n=== 槽位不同的样本（官方繁体文本 | 汉化按B解码文本）===")
for r in slot_mismatch:
    print("  [%04X.%04X]" % (r[0], r[1]))
    print("     官方: %s" % r[2][:70])
    print("     汉化: %s" % r[3][:70])

# 2) 汉化版按 B 解码：统计越界槽位与「可疑」文本
oob = 0
oob_chars = {}
sus = []
for i in range(count):
    try:
        _, _, sl, _ = slots(data, ptrs[i])
    except Exception:
        continue
    for s in sl:
        if s - 32 >= len(B) or s - 32 < 0:
            oob += 1
            oob_chars[s] = oob_chars.get(s, 0) + 1
    txt = to_text(sl, B)
    if "{" in txt and len(sus) < 15:
        sus.append(txt[:80])
print("\n汉化版按 B 解码：越界槽位出现 %d 次" % oob)
print("越界槽位值分布(前15):", sorted(oob_chars.items())[:15])
print("\n含越界标记的文本样本:")
for s in sus:
    print("   ", s)
