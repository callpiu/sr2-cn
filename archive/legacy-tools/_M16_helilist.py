# -*- coding: utf-8 -*-
# 决定性：从 exe 提取所有 ACT_HELI_* 字符串名，匹配中英文文本，
# 列出直升机突击活动的完整字幕集 + 每条的简体专属字
import sys, os, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
CN = os.path.join(G, "patch.vpp_pc")

# 1) 从 exe 提取 ACT_HELI_* 名字（宽字符 UTF-16LE）
with open(os.path.join(G, "SR2_pc.exe"), "rb") as f:
    exe = f.read()
names = set()
for m in re.finditer(rb"ACT_HELI_[A-Za-z0-9_]{3,60}", exe):
    s = m.group().decode("ascii", "ignore").rstrip(". ")
    if 8 < len(s) < 70:
        names.add(s)
names = sorted(names)
print("=== exe 中的 ACT_HELI_* 字符串名（%d 个）===" % len(names))
for n in names:
    print("  ", n)

# 2) 载入中英文表
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


vv = Vpp(VANILLA)
T = parse_charlist(vv.read(vv.find("charlist_CH", "txt")))
cn = Vpp(CN)
f = Vpp(CN)
d_cn = cn.read(cn.find("static_CH", "le_strings"))
B = parse_charlist(cn.read(cn.find("charlist_CH", "txt")))
BT = set(ord(c) for c in T)
missing = set(c for c in B if ord(c) not in BT and 0x4E00 <= ord(c) <= 0x9FFF)

d_us = vv.read(vv.find("static_US", "le_strings"))
bu, = struct.unpack_from("<H", d_us, 6)
cu, = struct.unpack_from("<I", d_us, 8)
pu = struct.unpack_from("<%dI" % cu, d_us, 12 + bu * 8)

# 英文表：名字在记录前的注释？不 —— text_tag 就是名字本身。
# SR2 的 le_strings 记录 = [id1][id2] + 文本。名字是 hash，不在表里。
# 所以用英文文本内容匹配（ACT_HELI 相关文案里含 heli/protection 等词）

def us_rec(p):
    id1, id2 = struct.unpack_from("<HH", d_us, p)
    q = p + 4
    end = q
    while end + 1 < len(d_us):
        if d_us[end] == 0 and d_us[end + 1] == 0:
            break
        end += 2
    return id1, id2, d_us[q:end].decode("utf-16-be", "replace")


def cn_rec(p):
    id1, id2 = struct.unpack_from("<HH", d_cn, p)
    q = p + 4
    out = []
    while True:
        s, = struct.unpack_from(">H", d_cn, q)
        q += 2
        if s == 0:
            break
        k = s - 32
        out.append(B[k] if 0 <= k < len(B) else "{%d}" % s)
    return id1, id2, "".join(out)


bc, = struct.unpack_from("<H", d_cn, 6)
cc, = struct.unpack_from("<I", d_cn, 8)
pc = struct.unpack_from("<%dI" % cc, d_cn, 12 + bc * 8)

usmap, cnmap = {}, {}
for i in range(cu):
    p = pu[i]
    if p + 6 > len(d_us):
        continue
    a, b_, s = us_rec(p)
    usmap[(a, b_)] = s
for i in range(cc):
    p = pc[i]
    if p + 6 > len(d_cn):
        continue
    a, b_, s = cn_rec(p)
    cnmap[(a, b_)] = s

# 3) 找英文含 heli + (protect|homie|escort|convoy) 的记录
print("\n=== 直升机突击相关字幕（英文含 heli 且含保护/护送语义）===")
KEY = re.compile(r"heli|convoy|escort|homie|protect|bomb", re.I)
rows = []
for k, en in usmap.items():
    if not KEY.search(en):
        continue
    if len(en) > 120:
        continue
    zh = cnmap.get(k, "")
    han = [c for c in zh if 0x4E00 <= ord(c) <= 0x9FFF]
    bad = [c for c in han if c in missing]
    rows.append((k, en, zh, len(bad), len(han), "".join(bad)))
rows.sort(key=lambda r: -r[3])
for k, en, zh, nb, tot, hi in rows:
    print("\n  [%04X.%04X] 缺字%d/%d: %s" % (k[0], k[1], nb, tot, hi))
    print("     英: %s" % en[:90])
    print("     中: %s" % zh[:90])
