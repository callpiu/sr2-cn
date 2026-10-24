# -*- coding: utf-8 -*-
# 验证：引擎索引 = 字符在「按代码页排序的字符表」中的名次
import sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2font import Font

f = Font(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
CL = f.charlist  # 汉化字符表（Unicode 升序）

# 9 组确凿对照（第一句）
PAIRS = [("你", "任"), ("的", "璨"), ("弟", "偶"), ("兄", "巧"), ("们", "位"),
         ("需", "雄"), ("要", "衡"), ("保", "伪"), ("护", "该")]
# 第二句补充（供交叉验证）
PAIRS2 = [("正", "校"), ("去", "勾"), ("进", "远"), ("行", "貌"), ("交", "乱"),
          ("易", "携"), ("他", "亡"), ("避", "通"), ("免", "像"), ("受", "匪"),
          ("到", "冰"), ("攻", "挺"), ("击", "拮")]


def key_of(cp, codec):
    try:
        return chr(cp).encode(codec)
    except Exception:
        return b"\xff\xff\xff"


for nm, codec in (("GBK(936)", "gbk"), ("Big5(950)", "big5")):
    arr = sorted(CL, key=lambda c: key_of(c, codec))
    print("\n=== 引擎表按 %s 排序 ===" % nm)
    hit = 0
    tot = 0
    for c, d in PAIRS + PAIRS2:
        tot += 1
        try:
            rank = arr.index(ord(c))
        except ValueError:
            print("   %s 不在表" % c)
            continue
        got = chr(CL[rank]) if rank < len(CL) else "?"
        mark = "OK" if got == d else "×"
        if got == d:
            hit += 1
        print("   %s rank=%-5d -> %s（期望 %s）%s" % (c, rank, got, d, mark))
    print("   命中 %d/%d" % (hit, tot))

# 另验：引擎表 = Unicode 排序时
print("\n=== 引擎表按 Unicode 排序（对照）===")
hit = 0
for c, d in PAIRS + PAIRS2:
    rank = CL.index(ord(c))
    got = chr(CL[rank])
    if got == d:
        hit += 1
print("   命中 %d/%d" % (hit, len(PAIRS + PAIRS2)))
