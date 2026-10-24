# -*- coding: utf-8 -*-
# 反推 22 字乱码句的源文本
# 假设A：槽位按官方繁体表 T 编码，引擎按简体表 B 解码
#   => 显示字 d = B[T.index(源字)]  =>  源字 = T[B.index(d)]
# 假设B：显示字 d = B[E(c)+5]，E(c) 为引擎表 L 索引
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
CN = os.path.join(G, "patch.vpp_pc") if False else r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
import os


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
cn = Vpp(CN)
T = parse_charlist(vv.read(vv.find("charlist_CH", "txt")))
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}
print("T = %d 项（官方繁体）  B = %d 项（汉化简体）" % (len(T), len(B)))

DISP = "任璨偶巧们校衡勾远藐乱携伪该亡们通像匪冰挺拮"
print("\n显示句（22字）:", DISP)
print("长度 =", len(DISP))

print("\n=== 假设A：源字 = T[B.index(显示字)] ===")
srcA = []
for d in DISP:
    if d in bidx:
        k = bidx[d]
        srcA.append(T[k] if k < len(T) else "?")
    else:
        srcA.append("?")
print("  反推A:", "".join(srcA))

print("\n=== 逐字 ===")
for i, d in enumerate(DISP, 1):
    k = bidx.get(d, -1)
    ta = T[k] if 0 <= k < len(T) else "?"
    print("  %2d 显示=%s(B序%d)  T[%d]=%s" % (i, d, k, k, ta))
