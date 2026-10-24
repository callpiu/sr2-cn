import os, re
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
print("=== 搜索引用 DFEngine / CreateDFEngine 的文件 ===")
for root, dirs, fs in os.walk(G):
    if any(x in root for x in ("_DLSS5_Backup","reshade-shaders","_archive")): continue
    for f in fs:
        p = os.path.join(root,f)
        try:
            if os.path.getsize(p) > 40*1024*1024: continue
            d = open(p,"rb").read()
        except Exception: continue
        for pat in (b"DFEngine.dll", b"CreateDFEngine", b"DFEngine"):
            if pat in d:
                print("  %-58s %-16s" % (os.path.relpath(p,G), pat.decode()))
                break
