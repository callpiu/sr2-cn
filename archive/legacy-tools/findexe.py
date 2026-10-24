import os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
KEYS = [b"SUI_OPTIONS_TITLE", b"SUI_LOADING", b"SUI_OPTIONS_WEAPON_SWITCH_SOUND"]
files = ["SR2_pc.exe","DFEngine.dll"]
# 也扫 juiced 目录
for root, dirs, fs in os.walk(G):
    for f in fs:
        if f.lower().endswith((".dll",".exe",".asi")):
            files.append(os.path.relpath(os.path.join(root,f), G))
files = sorted(set(files))
for rel in files:
    p = os.path.join(G, rel)
    if not os.path.exists(p): continue
    try: d = open(p,"rb").read()
    except Exception: continue
    found = [k.decode() for k in KEYS if k in d]
    if found:
        print("  %-46s %8d  含: %s" % (rel, len(d), " ".join(found)))
