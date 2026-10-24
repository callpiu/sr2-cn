import os, sys, hashlib
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
files = {
 "当前部署":        os.path.join(G,"patch.vpp_pc"),
 "v533_tagfix":     os.path.join(G,"patch.vpp_pc.v533_tagfix_20261012_131656.bak"),
 "v532_before_exp": os.path.join(G,"patch.vpp_pc.v532_before_exp.bak"),
 "v531_before_mirror": os.path.join(G,"patch.vpp_pc.v531_before_mirror.bak"),
}
info = {}
for lab, p in files.items():
    if not os.path.exists(p): print("  %s 不存在" % lab); continue
    v = Vpp(p)
    ent_c = v.find("charlist_CH","txt")
    ent_v = v.find("fnt_chinese","vf3_pc")
    ent_g = v.find("fnt_chinese","g_peg_pc")
    d = {e["name"]+"."+(e["ext"] or ""): e["size"] for e in v.entries()}
    info[lab] = (v.num, dict(d))
    print("%-22s %d 条目  %d 字节" % (lab, v.num, os.path.getsize(p)))
    for k in ("charlist_CH.txt","fnt_chinese.vf3_pc","fnt_chinese.g_peg_pc","static_CH.le_strings","static_US.le_strings"):
        print("    %-26s %s" % (k, d.get(k,"-")))
    print()
# 逐条比对 当前部署 vs v533_tagfix
if len(info) >= 2:
    labs = list(info)
    a, b = info[labs[0]][1], info[labs[1]][1]
    print("=== %s vs %s 条目差异 ===" % (labs[0], labs[1]))
    for k in sorted(set(a)|set(b)):
        if a.get(k) != b.get(k):
            print("    %-30s %s -> %s" % (k, a.get(k,"-"), b.get(k,"-")))
