# -*- coding: utf-8 -*-
# 决定性假设：引擎把字符转 GBK 字节，在「按 GBK 排序的表」中二分查找
# 找不到时返回插入点 -> 们/护 落到 362/2342
import sys, struct, bisect
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
print("T =", len(T), " B =", len(B))
TS, BS = set(T), set(B)

CON = {"你": 371, "的": 1836, "兄": 422, "弟": 1035, "需": 2667,
       "要": 2296, "保": 391, "们": 362, "护": 2342}

print("\n=== 们/护 是否在 T 中 ===")
for ch in "们护位该你兄弟需要保":
    print("  %s(U+%04X) 在T=%s  在B=%s  T序=%s B序=%s" % (
        ch, ord(ch), ch in TS, ch in BS,
        T.index(ch) if ch in TS else "-", B.index(ch) if ch in BS else "-"))


def gbk_sort_key(c):
    """能 GBK 编码的按字节排，否则排最后（按码点）"""
    try:
        return (0, c.encode("gbk"))
    except Exception:
        return (1, c.encode("utf-16-be"))


for tag, tab in (("B(汉化简体)", B), ("T(官方繁体)", T)):
    srt = sorted(tab, key=gbk_sort_key)
    keys = [gbk_sort_key(c) for c in srt]
    print("\n=== 按 GBK 排序的 %s（%d 项）===" % (tag, len(srt)))
    hit = 0
    for c, e in CON.items():
        if c not in tab:
            print("  %s 不在表中" % c); continue
        # 精确查找
        if srt[e] == c:
            hit += 1
            print("  %-4s 精确名次 %d == 引擎格 %d  ✓" % (c, e, e))
        else:
            # 二分插入点
            k = gbk_sort_key(c)
            pos = bisect.bisect_left(keys, k)
            print("  %-4s 引擎格=%d  精确名次=%s(=%s)  二分插入点=%d  %s" % (
                c, e, tab.index(c) if c in tab else "-", srt[e] if e < len(srt) else "OOB",
                pos, "✓ 插入点吻合" if pos == e else ""))
            if pos == e:
                hit += 1
    print("  命中 %d/%d" % (hit, len(CON)))
