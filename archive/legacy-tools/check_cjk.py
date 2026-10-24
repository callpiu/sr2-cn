import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
print("总项数 %d" % len(cn))
print("cn[1030] = %d = %s" % (cn[1030], chr(cn[1030])))
print("cn[250]  = %d = %s" % (cn[250], chr(cn[250])))
print("cn[1035] = %d = %s" % (cn[1035], chr(cn[1035])))
print()
print("ord('弟') = %d, 在表内: %s" % (ord('弟'), ord('弟') in cn))
print("ord('天') = %d, 在表内: %s" % (ord('天'), ord('天') in cn))
print("ord('甲') = %d, 在表内: %s" % (ord('甲'), ord('甲') in cn))
print()
# 统计 CJK 数量
cjk = [c for c in cn if 0x4e00 <= c <= 0x9fff]
print("CJK 码点数: %d" % len(cjk))
print("前 20 个 CJK: %s" % "".join(chr(c) for c in cjk[:20]))
print("第 1030 个 CJK 附近的索引: %s" % cjk[1025:1040])
