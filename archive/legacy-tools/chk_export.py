import sys, os
W = r"F:\sr2-cn"
# 用户导出的第三方字表
p1 = os.path.join(W,"_day_2026-10-07","04_规则与数据","字表_第三方简体_charlist_CH.txt")
raw = open(p1,"rb").read()
print("导出的第三方字表: %d 字节" % len(raw))
cps = [int(l) for l in raw.decode("utf-8").split("\n") if l.strip().isdigit()]
print("  解析出 %d 项 (文档说 2795)" % len(cps))
print("  前 10: %s" % cps[:10])
print("  末 10: %s" % "".join(chr(c) for c in cps[-10:]))
print()
# 与游戏里实际使用的比对
sys.path.insert(0, os.path.join(W,"pylibs")); sys.path.insert(0, W)
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
raw2 = bytes(v.read(v.find("charlist_CH","txt")))
cps2 = [int(l) for l in raw2.decode("utf-8").split("\n") if l.strip().isdigit()]
print("游戏里当前字表: %d 字节, %d 项" % (len(raw2), len(cps2)))
print("  与导出的完全相同: %s" % (cps == cps2))
print()
# 可读对照
p2 = os.path.join(W,"_day_2026-10-07","04_规则与数据","字表_第三方简体_可读对照.txt")
if os.path.exists(p2):
    print("可读对照 前 5 行:")
    with open(p2, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 5: break
            print("  %s" % line.rstrip())
