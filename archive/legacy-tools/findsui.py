import os
# 在 Juice 仓库和游戏目录里找含 SUI_LOADING_9 的文件
roots = [r"F:\sr2-cn\juicedsrc", r"G:\SteamLibrary\steamapps\common\Saints Row 2"]
KEYS = [b"SUI_LOADING_9", b"SUI_OPTIONS_TITLE"]
for R in roots:
    print("=== %s ===" % R)
    for root, dirs, fs in os.walk(R):
        for f in fs:
            p = os.path.join(root, f)
            try:
                if os.path.getsize(p) > 40*1024*1024: continue
                d = open(p,"rb").read()
            except Exception: continue
            hit = [k.decode() for k in KEYS if k in d]
            if hit:
                print("  %-62s %s" % (os.path.relpath(p,R), " ".join(hit)))
    print()
