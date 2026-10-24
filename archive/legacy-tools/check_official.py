import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc.official_bak"))
print("=== 官方版 patch.vpp_pc 的字符表内容（判断是简/繁/日）===")
d = bytes(v.read(v.find("charlist_CH","txt")))
cps = [int(l) for l in d.decode("utf-8","replace").split("\n") if l.strip().isdigit()]
# 繁简判别字：会/會 楼/樓 选/選 车/車
tests = {"会":0x4F1A,"會":0x6703,"楼":0x697C,"樓":0x6A13,"选":0x9009,"選":0x9078,"车":0x8F66,"車":0x8ECA,"龙":0x9F99,"龍":0x9F8D}
print("  条目数: %d" % len(cps))
for ch, cp in tests.items():
    print("    %s U+%04X: %s" % (ch, cp, "在表内" if cp in cps else "不在"))
print()
print("  前 20 个码点: %s" % ["U+%04X" % x for x in cps[:20]])
print()
# 官方 static_US 里是否含中文
print("=== 官方 static_US 是否含中文文本 ===")
e = v.find("static_US","le_strings")
d2 = bytes(v.read(e))
# 找 UTF-16 中文
import re
u = d2.decode("utf-16-le","ignore")
zh = re.findall(r'[\u4e00-\u9fff]{2,}', u)
print("  含中文字串: %d 个，前 5: %s" % (len(zh), zh[:5]))
print()
print("=== 汉化版 static_CH 前几条（确认是简体）===")
v2 = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v2.read(v2.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
print("  汉化版 charlist_CH 条目数: %d" % len(CPS))
for ch, cp in tests.items():
    print("    %s U+%04X: %s" % (ch, cp, "在表内" if cp in CPS else "不在"))
