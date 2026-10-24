# -*- coding: utf-8 -*-
# 决定性检验：g(c) = B.index( T[插入点] ) ？
# 们: 插入点305 -> T[305]=仰(U+4EF0) -> B.index(仰) =? 362
# 护: 插入点1120 -> T[1120]=披(U+62AB) -> B.index(披) =? 2342
import sys, bisect
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
Tcps = [ord(c) for c in T]
Bidx = {c: i for i, c in enumerate(B)}
CON = {"你": 371, "的": 1836, "兄": 422, "弟": 1035, "需": 2667,
       "要": 2296, "保": 391, "们": 362, "护": 2342}

print("=== 检验 g(c) = B.index(T[插入点]) ===")
for c, e in CON.items():
    cp = ord(c)
    p = bisect.bisect_left(Tcps, cp)
    tchar = T[p] if p < len(T) else "(末尾)"
    bidx = Bidx.get(tchar, -1)
    print("  %s(U+%04X) 插入点=%d T[%d]=%s(U+%04X) B.index=%d  引擎格=%d  %s" % (
        c, cp, p, p, tchar, ord(tchar), bidx, e,
        "★吻合" if bidx == e else ""))

# 也检验插入点-1
print("\n=== 检验 g(c) = B.index(T[插入点-1]) ===")
for c, e in CON.items():
    cp = ord(c)
    p = bisect.bisect_left(Tcps, cp) - 1
    tchar = T[p] if 0 <= p < len(T) else "(越界)"
    bidx = Bidx.get(tchar, -1)
    print("  %s(U+%04X) T[%d]=%s(U+%04X) B.index=%d  引擎格=%d  %s" % (
        c, cp, p, tchar, ord(tchar), bidx, e, "★吻合" if bidx == e else ""))

# 全表：B 中不在 T 的字，按此模型预测引擎格，看分布是否合理
BT = set(Tcps)
notInT = [c for c in B if ord(c) not in BT]
print("\n=== 不在 T 的 %d 个字的预测引擎格分布 ===" % len(notInT))
pred = []
for c in notInT:
    p = bisect.bisect_left(Tcps, ord(c))
    t = T[p] if p < len(T) else None
    if t and t in Bidx:
        pred.append((c, Bidx[t]))
vals = [v for _, v in pred]
print("可预测 %d 个，值范围 %d..%d" % (len(pred), min(vals), max(vals)))
print("样例 20 个:", pred[:20])
