import os, re
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
M = os.path.join(G,"Mods")
# 找所有 SUI_TIPS_ / SUI_LOADING_ 引用
for f in sorted(os.listdir(M)):
    if not f.endswith(".lua"): continue
    p = os.path.join(M,f)
    s = open(p, encoding="utf-8", errors="replace").read()
    ks = sorted(set(re.findall(r'"SUI_(?:TIPS|LOADING)_[A-Z0-9_]+"', s)))
    if ks:
        print("%-24s %d 个:" % (f, len(ks)))
        for k in ks[:20]: print("    %s" % k)
