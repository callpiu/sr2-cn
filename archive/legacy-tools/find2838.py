# -*- coding: utf-8 -*-
"""找 2838 字表：显式列出每个容器的 charlist 类条目。"""
import sys, os, struct, glob
sys.path.insert(0, r"F:/sr2-cn")
sys.path.insert(0, r"F:/sr2-cn/stub")
import sr2lib
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
allcps = {}
for path in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    name = os.path.basename(path)
    print("\n### %s (%d B)" % (name, os.path.getsize(path)))
    try:
        vp = sr2lib.Vpp(path)
    except Exception as e:
        print("  打不开:", e)
        continue
    n = 0
    for e in vp.entries():
        n += 1
        nm = e["name"]
        if "charlist" in nm.lower() or "char" in nm.lower() and "list" in nm.lower():
            try:
                d = vp.read(e)
                lines = [int(l) for l in d.decode("utf-8").split("\n")
                         if l.strip().isdigit()]
                tag = ""
                if lines:
                    tag = " 数字行=%d 首=%d 末=%d" % (len(lines), lines[0], lines[-1])
                    allcps["%s::%s" % (name, nm)] = lines
                print("  %-30s.%-8s %8d B%s" % (nm, e["ext"], e["size"], tag))
            except Exception as ex:
                print("  %-30s.%-8s %8d B  读失败: %s" % (nm, e["ext"], e["size"], ex))
    print("  （共 %d 条目）" % n)

# 若找到多张表，对比坏字/好字
BAD = {"会": 348, "三": 239, "律": 1057, "徒": 1058, "得": 1059,
       "必": 1066, "联": 2100}
DISP = {"会": "伙", "三": "丈", "律": "延", "徒": "建", "得": "开",
        "必": "弗", "联": "?"}
GOOD = {"人": 344, "帮": 992, "计": 2312, "赚": 2405}
base = allcps.get("patch.vpp_pc::charlist_CH.txt")
if base:
    for k, lst in allcps.items():
        if k.endswith("charlist_CH.txt") and len(lst) == 2795:
            continue
        m = {cp: i for i, cp in enumerate(lst)}
        print("\n[%s] n=%d" % (k, len(lst)))
        for ch, i in list(BAD.items()) + list(GOOD.items()):
            cp = base[i]
            j = m.get(cp, -1)
            extra = ""
            if 0 <= j < len(lst):
                extra = " → 该位置的字 = %s (显示=%s) %s"
                extra = extra % (chr(lst[j]), DISP.get(ch, "?"),
                                 "★命中!" if chr(lst[j]) == DISP.get(ch) else "")
            print("   %s idx2795=%-5d idx该表=%-6d%s" % (ch, i, j, extra))
