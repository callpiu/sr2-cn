# -*- coding: utf-8 -*-
"""验证：运行时是否用另一张字表（如 2838 项）→ idx 漂移解释坏字位。"""
import sys, os, struct, glob
sys.path.insert(0, r"F:/sr2-cn")
sys.path.insert(0, r"F:/sr2-cn/stub")
import sr2lib
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# 1) 全容器找形如字表的文本资源（全是数字行）
print("=== 搜索所有容器中的字表类文本 ===")
tables = {}   # name -> (container, count)
for path in glob.glob(os.path.join(G, "*.vpp_pc")):
    name = os.path.basename(path)
    try:
        vp = sr2lib.Vpp(path)
    except Exception as e:
        print("  %s 打不开: %s" % (name, e))
        continue
    for e in vp.entries():
        try:
            d = vp.read(e)
        except Exception:
            continue
        if len(d) > 40 and len(d) < 60000:
            try:
                t = d.decode("utf-8")
            except Exception:
                continue
            lines = [l for l in t.split("\n") if l.strip().isdigit()]
            if lines and len(lines) > 200:
                key = "%s::%s.%s" % (name, e["name"], e.get("ext", ""))
                tables[key] = len(lines)
                print("  %-50s %5d 行" % (key, len(lines)))

# 2) 载入各表，算坏字/好字在每张表中的 idx
CPS = {}
for path in glob.glob(os.path.join(G, "*.vpp_pc")):
    name = os.path.basename(path)
    try:
        vp = sr2lib.Vpp(path)
    except Exception:
        continue
    for e in vp.entries():
        try:
            d = vp.read(e)
        except Exception:
            continue
        if len(d) > 40 and len(d) < 60000:
            try:
                t = d.decode("utf-8")
            except Exception:
                continue
            lines = [int(l) for l in t.split("\n") if l.strip().isdigit()]
            if len(lines) > 200:
                CPS["%s::%s" % (name, e["name"])] = lines

# 已知坏字位（字: idx2795）与好字位
BAD = {"会": 348, "三": 239, "律": 1057, "徒": 1058, "得": 1059,
       "心": 1065, "必": 1066, "联": 2100}
GOOD = {"人": 344, "帮": 992, "赚": 2405, "计": 2312, "社": 1908,
        "老": 268, "郊": 30, "主": 751, "城": 237}

print("\n=== 各表中同一字的 idx 对比（2795 表为基准）===")
base = None
for k, v in CPS.items():
    if len(v) == 2795:
        base = k
for k, lst in sorted(CPS.items()):
    m = {cp: i for i, cp in enumerate(lst)}
    print("\n[%s] n=%d" % (k, len(lst)))
    for ch, i in list(BAD.items()) + list(GOOD.items()):
        cp = CPS[base][i]
        j = m.get(cp, -1)
        mark = "★坏" if ch in BAD else "好"
        print("   %s(%s) idx2795=%-5d idx该表=%-6d 差=%s"
              % (ch, mark, i, j, (j - i) if j >= 0 else "无"))
