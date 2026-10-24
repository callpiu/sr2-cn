import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cps = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
IDX = {chr(cp): i for i, cp in enumerate(cps)}
pairs = [("你","任"),("的","璨"),("弟","偶"),("兄","巧"),("们","位"),("需","雄"),("要","衡"),
         ("保","伪"),("护","该"),("出","衡"),("去","勾"),("谈","远"),("几","藐"),("笔","乱"),
         ("生","携"),("意","伪"),("他","通"),("免","匪"),("遭","冰"),("袭","挺"),("击","拮")]
print("  %-4s %-6s %-4s %-6s %-7s %s" % ("源","idx","乱码","idx","差","说明"))
diffs = []
for a, b in pairs:
    if a in IDX and b in IDX:
        d = IDX[b] - IDX[a]
        diffs.append(d)
        print("  %-4s %-6d %-4s %-6d %+7d" % (a, IDX[a], b, IDX[b], d))
    else:
        print("  %-4s %-6s %-4s %-6s %7s  %s" % (a, IDX.get(a,"缺"), b, IDX.get(b,"缺"), "-", "有字不在表内"))
print()
print("差值: %s" % diffs)
print("不同差值: %s" % sorted(set(diffs)))
print("平均: %.1f" % (sum(diffs)/len(diffs)))
