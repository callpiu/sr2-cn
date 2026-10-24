import os, shutil
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
M = os.path.join(G,"Mods")
FILES = ["pause_menu.lua","main_menu.lua","sui_main_menu.lua","hud.lua","city_load.lua"]
print("=== 回退到原始版本（.before_sui_cn，纯 ASCII）===")
for fn in FILES:
    src = os.path.join(M, fn + ".before_sui_cn")
    dst = os.path.join(M, fn)
    if not os.path.exists(src):
        print("  %-24s 缺少原始备份" % fn); continue
    shutil.copy2(src, dst)
    b = open(dst,"rb").read()
    try:
        b.decode("ascii"); enc = "纯 ASCII"
    except UnicodeDecodeError:
        enc = "含非ASCII"
    print("  %-24s %8d 字节  %s  OK" % (fn, len(b), enc))
print()
# 复验：确认没有残留的乱码字节
print("=== 复验：不应再有非 ASCII 字节 ===")
for fn in FILES:
    b = open(os.path.join(M,fn),"rb").read()
    na = sum(1 for x in b if x > 0x7F)
    print("  %-24s 非ASCII 字节 %d %s" % (fn, na, "OK" if na == 0 else "★ 仍有残留"))
print()
print("=== 备份文件保留（可随时取用）===")
for fn in FILES:
    for suf in (".before_sui_cn",".utf8"):
        p = os.path.join(M,fn+suf)
        if os.path.exists(p): print("  %s" % os.path.basename(p))
