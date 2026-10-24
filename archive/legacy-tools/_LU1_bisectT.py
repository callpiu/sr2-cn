# -*- coding: utf-8 -*-
# 决定性假设：引擎取格 = B.index(c)，但对「不在官方繁体表 T 中」的字，
# 引擎在 T（按码点排序）中二分查找 -> 返回插入点（不是精确索引）
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
Tcps = [ord(c) for c in T]           # T 按码点递增（已验）
CON = {"你": 371, "的": 1836, "兄": 422, "弟": 1035, "需": 2667,
       "要": 2296, "保": 391, "们": 362, "护": 2342}

print("T=%d(码点递增=%s)  B=%d" % (len(T), all(Tcps[i] < Tcps[i+1] for i in range(len(T)-1)), len(B)))
print()
print("%-4s %-8s %-8s %-8s %-8s %-8s %s" % ("字", "U+", "在T?", "T精确", "T插入点", "引擎格", "判定"))
for c, e in CON.items():
    cp = ord(c)
    inT = cp in set(Tcps)
    exact = Tcps.index(cp) if inT else -1
    ins = bisect.bisect_left(Tcps, cp)
    # 引擎格 = ?
    pred = None
    if inT:
        pred = "在T -> 用 B.index"
    else:
        pred = "不在T -> 插入点?"
    mark = ""
    if not inT and ins == e:
        mark = "★ 插入点吻合引擎格!"
    elif inT and B.index(c) == e:
        mark = "✓ 在T用B.index正确"
    print("%-4s %-8X %-8s %-8d %-8d %-8d %s  %s" % (c, cp, inT, exact, ins, e, pred, mark))

# 全表扫描：若模型成立，「不在T的字」其引擎格应 = T插入点
# 用 B 中所有不在 T 中的字做统计
BT = set(Tcps)
notInT = [c for c in B if ord(c) not in BT]
print("\nB 中不在 T 中的字数 =", len(notInT))
print("样例:", "".join(notInT[:40]))
# 这些字的 T 插入点分布
ins_pts = [bisect.bisect_left(Tcps, ord(c)) for c in notInT]
print("插入点范围 =", min(ins_pts), "..", max(ins_pts))
print("们 的插入点 =", bisect.bisect_left(Tcps, 0x4EEC), " 护 的插入点 =", bisect.bisect_left(Tcps, 0x62A4))
# 插入点附近的 T 字符
for cp, name in ((0x4EEC, "们"), (0x62A4, "护")):
    p = bisect.bisect_left(Tcps, cp)
    print("  %s(U+%04X) 插入点=%d  T[%d]=U+%04X(%s)  T[%d]=U+%04X(%s)" % (
        name, cp, p, p - 1, Tcps[p - 1], chr(Tcps[p - 1]), p, Tcps[p], chr(Tcps[p])))
