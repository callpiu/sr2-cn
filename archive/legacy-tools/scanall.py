import os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
KEYS = [b"SUI_OPTIONS_TITLE", b"SUI_LOADING", b"SUI_OPTIONS_WEAPON_SWITCH_SOUND", b"SUI_OPTIONS"]
hits = {}
for root, dirs, fs in os.walk(G):
    for f in fs:
        p = os.path.join(root, f)
        try: sz = os.path.getsize(p)
        except Exception: continue
        if sz > 60*1024*1024: continue
        try: d = open(p,"rb").read()
        except Exception: continue
        for k in KEYS:
            if k in d:
                hits.setdefault(k.decode(), []).append((os.path.relpath(p,G), sz))
for k, lst in hits.items():
    print("=== %s (%d 个文件) ===" % (k, len(lst)))
    for rel, sz in lst[:10]: print("    %-56s %9d" % (rel, sz))
if not hits: print("全盘未找到 —— 说明是运行期构造的")
