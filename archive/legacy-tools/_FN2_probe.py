"""FN2: several decisive probes.
1. atlas column count: is the right edge (x>=2016) used?  (65 vs 66 cols)
2. slots of the s2 rendered chars
3. GBK / Big5 ordering hypotheses
"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
import numpy as np
from sr2lib import Vpp, dxt3_decode

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = cl(os.path.join(G, "patch.vpp_pc"), "charlist_CH")
v = Vpp(os.path.join(G, "textures.vpp_pc"))
rgb, alpha = dxt3_decode(v.read(v.find("fnt_chinese")), 2048, 2048)

print("== 1. atlas right edge ==")
for x0 in (2000, 2016, 2040):
    reg = alpha[:, x0:x0+8]
    print("  x=%d..%d  max=%d  nonzero=%d" % (x0, x0+8, reg.max(), (reg > 20).sum()))
# rows beyond 65-col capacity
print("  last row y=%d..%d max=%d" % (1+31*42, 1+31*42+31, alpha[1+31*42:1+31*42+31, :].max()))

print()
print("== 2. slots of rendered chars ==")
def slot(ch):
    return M.index(ch) if ch in M else -1
S2 = "任璨偶巧位校衡勾远藐乱携伪该亡位通像匪冰挺拮"
S2C = "你的弟兄们要出去谈几笔生意，保护他们免遭袭击"
for a, b in zip(S2C, S2):
    print("   U+%04X %s -> U+%04X %s   slot=%-5d  code=%d" % (
        ord(a), a, ord(b), b, slot(b), slot(a) + 32))

print()
print("== 3. GBK / Big5 ordering ==")
def enc_order(cp, enc):
    try:
        return bytes(chr(cp), enc)
    except Exception:
        return None

for enc in ("gbk", "big5", "gb18030"):
    lst = [c for c in M if enc_order(c, enc) is not None]
    lst.sort(key=lambda c: enc_order(c, enc))
    pos = {c: i for i, c in enumerate(lst)}
    ok = 0
    line = []
    for corr, scr in [(0x4F60, 0x4EFB), (0x7684, 0x74A8), (0x5F1F, 0x5076), (0x5144, 0x5DE7),
                      (0x4EEC, 0x4F4D), (0x9700, 0x96C4), (0x8981, 0x8861), (0x4FDD, 0x4F2A), (0x62A4, 0x8BE5)]:
        i = pos.get(corr, -1)
        j = slot(scr)
        hit = (i == j)
        ok += hit
        line.append("%s->%s(%d/%d)" % (chr(corr), chr(scr), i, j))
    print("  %-8s %d/9  %s" % (enc, ok, " ".join(line)))
