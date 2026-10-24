import os, re, struct
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
d = open(os.path.join(G,"SR2_pc.exe"),"rb").read()
print("SR2_pc.exe %d 字节" % len(d))
for n in (b"CreateDFEngine", b"RegisterVintLuaHookString", b"UnregisterVintLuaHookString", b"DFEngine"):
    i = d.find(n)
    print("  %-26s %s" % (n.decode(), ("0x%X" % i) if i>=0 else "未找到"))
print()
# 看 CreateDFEngine 的上下文（是不是导入表项）
i = d.find(b"CreateDFEngine")
print("CreateDFEngine 上下文:")
print("  %r" % d[max(0,i-64):i+64])
print()
# 是否在导入表里？找 DLL 名的相邻关系
i2 = d.find(b"DFEngine")
if i2 >= 0:
    print("DFEngine 上下文:")
    print("  %r" % d[max(0,i2-64):i2+64])
print()
# 对比未打补丁的 exe
u = open(os.path.join(G,"sr2_pc_unpatched.exe"),"rb").read()
print("sr2_pc_unpatched.exe %d 字节" % len(u))
print("  含 CreateDFEngine: %s" % (b"CreateDFEngine" in u))
print("  含 DFEngine:       %s" % (b"DFEngine" in u))
print()
# 找可能的 ASI loader / 代理
print("=== 搜索 Juiced 加载器特征串 ===")
for root, dirs, fs in os.walk(G):
    if any(x in root for x in ("_DLSS5_Backup","reshade-shaders","_archive","Juiced\\logs")): continue
    for f in fs:
        p = os.path.join(root,f)
        try:
            if os.path.getsize(p) > 40*1024*1024: continue
            dd = open(p,"rb").read()
        except Exception: continue
        for pat in (b"Juiced Loader", b"juiced loader", b"ASI Loader", b"Ultimate ASI", b"CreateDFEngine"):
            if pat in dd and not f.lower().endswith((".log",".txt",".dll")):
                print("  %-56s %s" % (os.path.relpath(p,G), pat.decode()))
                break
