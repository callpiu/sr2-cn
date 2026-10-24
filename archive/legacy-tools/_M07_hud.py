# -*- coding: utf-8 -*-
# 找「走字幕路径」的验证句：HUD 目标提示（非任务对白、非菜单）
# 重点：直升机突击相关目标提示（用户正在做这个活动，最容易触发）
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

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


vv, cn = Vpp(VANILLA), Vpp(CN)
T = parse_charlist(vv.read(vv.find("charlist_CH", "txt")))
f = Font(CN)
B = [chr(c) for c in f.charlist]
BT = set(ord(c) for c in T)
missing = set(c for c in B if ord(c) not in BT and 0x4E00 <= ord(c) <= 0x9FFF)


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


d, count, ptrs = load("static_CH")
allrec = []
for i in range(count):
    p = ptrs[i]
    if p + 6 > len(d):
        continue
    try:
        a, b_, t = rec(d, p)
    except Exception:
        continue
    allrec.append((a, b_, t))

# 1) 直升机突击相关
print("=== 直升机突击 / 目标提示（HUD 字幕路径）===")
for a, b_, t in allrec:
    if ("直升" in t or "支援" in t) and len(t) < 60:
        han = [c for c in t if 0x4E00 <= ord(c) <= 0x9FFF]
        bad = [c for c in han if c in missing]
        print("  [%04X.%04X] 「%s」  缺字%d/%d: %s" % (a, b_, t, len(bad), len(han), "".join(bad)))

# 2) 通用 HUD 目标提示：短、纯中文、含高频缺字
print("\n=== 高频缺字的短目标提示（做任务必现）===")
cands = []
for a, b_, t in allrec:
    han = [c for c in t if 0x4E00 <= ord(c) <= 0x9FFF]
    if not (4 <= len(han) <= 24):
        continue
    if any(x in t for x in ("%", "{", "$", "img", "color", "format", "[")):
        continue
    bad = [c for c in han if c in missing]
    if len(bad) >= 2:
        cands.append((len(bad) / len(han), len(bad), len(han), a, b_, t, "".join(sorted(set(bad)))))
cands.sort(reverse=True)
for r, nb, tot, a, b_, t, hi in cands[:25]:
    print("  [%04X.%04X] 「%s」  缺字%d/%d: %s" % (a, b_, t, nb, tot, hi))
