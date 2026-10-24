# -*- coding: utf-8 -*-
# 假设：引擎取格 = 槽位 - 5（漏减 32），显示字 = B[槽位-5] = B[B.index(源字)+27]
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font, Vpp

CN = r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc"
cn = Vpp(CN)
f = Font(CN)
B = [chr(c) for c in f.charlist]
bidx = {c: i for i, c in enumerate(B)}

SRC = "好了，咱们离开这儿吧……"
DISP = "任璨偶巧们校衡勾远藐乱携"

print("=== 假设：显示字 = B[B.index(源字) + 27] ===")
ok = 0
for i, (c, d) in enumerate(zip(SRC, DISP), 1):
    bi = bidx.get(c, -1)
    pred = B[bi + 27] if 0 <= bi + 27 < len(B) else "?"
    m = "★命中" if pred == d else ""
    if pred == d:
        ok += 1
    print("  %2d %s(B序%-5d) -> 预测%s  实际%s  %s" % (i, c, bi, pred, d, m))
print("命中 %d/%d" % (ok, len(SRC)))

print("\n=== 换偏移量 D 全扫 ===")
for D in range(-60, 61):
    hit = sum(1 for c, d in zip(SRC, DISP)
              if c in bidx and 0 <= bidx[c] + D < len(B) and B[bidx[c] + D] == d)
    if hit >= 6:
        print("  D=%+d 命中 %d/%d" % (D, hit, len(SRC)))

# 也检验第二行
SRC2 = "伪该亡们通像匪冰挺拮"
print("\n=== 第二行（若源文本已知可验证）===")

# 另一假设：显示字 = B[槽位-5]，槽位按 T 编码
# 槽位 = T.index(源字)+32 => 显示 = B[T.index(源字)+27]
print("\n=== 假设：槽位按 T 编码，显示 = B[T.index(源字)+27] ===")
VANILLA = r"F:/sr2-cn/_backup_VANILLA/patch.vpp_pc.vanilla_20261017"
vv = Vpp(VANILLA)
def parse_charlist(raw):
    out = []
    for L in raw.split(b"\r\n"):
        s = L.strip()
        if not s or s.startswith(b"//") or s.startswith(b"count="): continue
        for tok in s.split():
            if tok.isdigit(): out.append(chr(int(tok)))
    return out
T = parse_charlist(vv.read(vv.find("charlist_CH", "txt")))
Tidx = {c: i for i, c in enumerate(T)}
for D in range(-60, 61):
    hit = 0
    for c, d in zip(SRC, DISP):
        ti = Tidx.get(c, -1)
        if ti >= 0 and 0 <= ti + D < len(B) and B[ti + D] == d:
            hit += 1
    if hit >= 6:
        print("  D=%+d 命中 %d/%d" % (D, hit, len(SRC)))
