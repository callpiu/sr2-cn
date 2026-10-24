import os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
M = os.path.join(G,"Mods")
print("=== 各文件的备份链 ===")
for fn in ("pause_menu.lua","main_menu.lua","sui_main_menu.lua","hud.lua","city_load.lua"):
    print("  %s:" % fn)
    for suf in ("", ".before_sui_cn", ".utf8", ".utf8.bak"):
        p = os.path.join(M, fn+suf)
        if os.path.exists(p):
            b = open(p,"rb").read()
            # 判定编码
            try: b.decode("utf-8"); enc="UTF-8"
            except UnicodeDecodeError:
                try: b.decode("gbk"); enc="GBK"
                except UnicodeDecodeError: enc="未知"
            na = sum(1 for x in b if x > 0x7F)
            print("      %-28s %8d 字节  %-6s 非ASCII %3d" % (fn+suf, len(b), enc, na))
