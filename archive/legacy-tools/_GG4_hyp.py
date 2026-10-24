# -*- coding: utf-8 -*-
"""GG4: 检验假设 —— 引擎用「官方字符表」而非汉化字符表做 槽位->字形 换算。"""
import sys, os
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
HAN = Vpp(os.path.join(G, "patch.vpp_pc"))
ORIG = Vpp(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")

def cl(v, nm="charlist_CH"):
    e = v.find(nm, "txt")
    return [int(s) for s in v.read(e).decode("utf-8", "replace").replace("\r", "\n").split("\n") if s.strip().isdigit()]

TH = cl(HAN)     # 汉化 2795
TO = cl(ORIG)    # 官方 2838
print("汉化 charlist=%d  官方 charlist=%d" % (len(TH), len(TO)))
po = {}
for i, c in enumerate(TO):
    po.setdefault(c, i)
ph = {}
for i, c in enumerate(TH):
    ph.setdefault(c, i)

# (槽位, 观测渲染字)
OBS = [
    (403, "任"), (1868, "璨"), (1067, "偶"), (454, "巧"), (364, "位"),
    (2699, "雄"), (2328, "衡"), (423, "伪"), (1222, "该"),
    (510, "衡"), (613, "勾"), (2389, "远"), (502, "藐"), (1995, "乱"),
    (1824, "携"), (356, "亡"), (460, "通"), (2563, "像"), (2312, "匪"), (479, "冰"),
]

print("\n%-6s %-6s %-10s %-12s %-12s %-8s" % ("槽位", "渲染", "汉化解出", "官方idx(该字)", "官方cell", "观测cell"))
ok = 0
for slot, got in OBS:
    i = slot - 32
    if not (0 <= i < len(TH)):
        print("  槽位 %d 越界" % slot); continue
    ch = chr(TH[i])
    oi = po.get(TH[i])
    hyp = (oi + 32) if oi is not None else None
    obs = ph.get(ord(got))
    obc = (obs + 32) if obs is not None else None
    hit = (hyp == obc)
    ok += hit
    print("%-6d %-6s %-10s %-12s %-12s %-8s %s" % (slot, got, ch, oi, hyp, obc, "命中" if hit else ""))
print("\n假设命中: %d/%d" % (ok, len(OBS)))
