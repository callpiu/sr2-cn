import os, sys
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
pats = [b"zSHP", b"zshp", b"SHP", b"Zshp"]
print("=== 在游戏目录搜索 zSHP / SHP ===")
n=0
for root, dirs, fs in os.walk(G):
    if "_archive" in root or "reshade-shaders" in root or "_DLSS5" in root: continue
    for f in fs:
        p = os.path.join(root,f)
        try:
            if os.path.getsize(p) > 20*1024*1024: continue
            d = open(p,"rb").read()
        except Exception: continue
        for pat in (b"zSHP", b"Zshp", b"Z_SHP"):
            if pat in d:
                print("  %-64s %s @0x%X" % (os.path.relpath(p,G), pat.decode(), d.find(pat)))
                n += 1
                break
        if n > 20: break
    if n > 20: break
print("  共 %d 个文件" % n)
print()
# 搜「SHP」在 mods 的 lua 里
print("=== mods 的 lua 里含 SHP 的 ===")
M = os.path.join(G,"Mods")
for f in sorted(os.listdir(M)):
    if not f.endswith(".lua"): continue
    try: s = open(os.path.join(M,f), encoding="latin1").read()
    except Exception: continue
    if "SHP" in s:
        for line in s.split("\n"):
            if "SHP" in line:
                print("  %-24s %s" % (f, line.strip()[:100]))
                break
