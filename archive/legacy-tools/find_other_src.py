import os, re, struct
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
H1, H2 = 0x84F287ED, 0x10AF1E62
pat = struct.pack("<I", H1)
print("=== 全盘搜索：哪些文件含 hash 0x%08X ===" % H1)
n = 0
for root, dirs, fs in os.walk(G):
    if any(x in root for x in ("_DLSS5_Backup","reshade-shaders","_vanilla_test","_probe")): continue
    for f in fs:
        p = os.path.join(root, f)
        try:
            if os.path.getsize(p) > 300*1024*1024: continue
            d = open(p,"rb").read()
        except Exception: continue
        if pat in d:
            print("  %-70s @0x%X" % (os.path.relpath(p,G), d.find(pat)))
            n += 1
print("  共 %d 个文件" % n)
print()
print("=== 搜索松散/其它位置的 static_CH* ===")
for root, dirs, fs in os.walk(G):
    for f in fs:
        if "static_ch" in f.lower() or (f.lower().startswith("patch") and f.lower().endswith(".vpp_pc")):
            p = os.path.join(root,f)
            print("  %-70s %d 字节" % (os.path.relpath(p,G), os.path.getsize(p)))
