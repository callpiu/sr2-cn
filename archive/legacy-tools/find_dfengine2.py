import os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
print("=== 全盘搜索 DFEngine.dll / DfEngine.dll（含所有副本）===")
for root, dirs, fs in os.walk(G):
    for f in fs:
        if f.lower() == "dfengine.dll":
            p = os.path.join(root,f)
            print("  %-64s %9d 字节  %s" % (os.path.relpath(p,G), os.path.getsize(p), __import__("datetime").datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M")))
print()
# 也搜 Steam 目录（可能有 Steam 备份/其他安装）
S = r"G:\SteamLibrary\steamapps"
print("=== Steam 目录下的 SR2 相关 ===")
for root, dirs, fs in os.walk(S):
    if root.count(os.sep) - S.count(os.sep) > 4: 
        dirs[:] = []
        continue
    for f in fs:
        if f.lower() in ("dfengine.dll","sr2_pc.exe"):
            p = os.path.join(root,f)
            print("  %-80s %9d" % (p, os.path.getsize(p)))
