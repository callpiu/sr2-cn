# -*- coding: utf-8 -*-
# 系统性验证：若「不在官方繁体表 T 中的字 -> 乱码」成立，
# 则字幕中含 B-T 字越多的句子，乱码应越多。
# 找出字幕里 B-T 字最密集的句子，供用户在游戏里验证
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


vv, cn = Vpp(VANILLA), Vpp(CN)
T = parse_charlist(vv.read(vv.find("charlist_CH", "txt")))
B = parse_charlist(cn.read(cn.find("charlist_CH", "txt")))
BT = set(ord(c) for c in T)
BTset = set(T)
missing = set(c for c in B if ord(c) not in BT)
print("B=%d  T=%d  不在T中的字数(B-T)=%d" % (len(B), len(T), len(missing)))

# 排除纯标点/ASCII，只看汉字
missing_han = set(c for c in missing if 0x4E00 <= ord(c) <= 0x9FFF)
print("其中汉字 =", len(missing_han))


def load(v, name):
    d = v.read(v.find(name, "le_strings"))
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
        out.append(s)
    return id1, id2, out


def txt(sl):
    r = []
    for s in sl:
        i = s - 32
        r.append(B[i] if 0 <= i < len(B) else "{%d}" % s)
    return "".join(r)


# 扫所有字幕文本，按 B-T 汉字密度排序
cands = []
for name in ("voice_script_CH", "static_CH"):
    d, count, ptrs = load(cn, name)
    for i in range(count):
        try:
            a, b_, sl = rec(d, ptrs[i])
        except Exception:
            continue
        t = txt(sl)
        han = [c for c in t if 0x4E00 <= ord(c) <= 0x9FFF]
        if len(han) < 5:
            continue
        bad = [c for c in han if c in missing_han]
        if not bad:
            continue
        cands.append((len(bad) / len(han), len(bad), len(han), a, b_, t, "".join(bad)))

cands.sort(reverse=True)
print("\n=== B-T 字密度最高的 25 条字幕（供游戏内验证）===")
for r, n, tot, a, b_, t, bad in cands[:25]:
    print("  [%04X.%04X] %d/%d 字是B-T  缺字=%s" % (a, b_, n, tot, bad))
    print("      %s" % t[:76])

print("\n=== 全字幕 B-T 汉字出现总次数 ===")
tot_bad = sum(r[1] for r in cands)
tot_han = sum(r[2] for r in cands)
print("  %d / %d (%.1f%%)" % (tot_bad, tot_han, 100.0 * tot_bad / tot_han))

# 频次表
from collections import Counter
cnt = Counter()
for r in cands:
    for c in r[6]:
        cnt[c] += 1
print("\n  B-T 汉字频次 Top30:", " ".join("%s(%d)" % (c, n) for c, n in cnt.most_common(30)))
