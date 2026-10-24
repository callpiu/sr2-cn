import os
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
M = os.path.join(G,"Mods")
for fn in ("pause_menu.lua","main_menu.lua","sui_main_menu.lua","hud.lua","city_load.lua"):
    p = os.path.join(M,fn)
    b = open(p,"rb").read()
    print("=== %s (%d 字节) ===" % (fn, len(b)))
    # 找第一段非 ASCII 字节并解码确认
    for i in range(len(b)):
        if b[i] > 0x7F:
            ctx = b[max(0,i-30):i+20]
            try:
                print("  首个非ASCII @%d: %r" % (i, ctx.decode("gbk","replace")))
            except Exception as e:
                print("  %r" % ctx)
            break
    # UTF-8 解出来会失败吗
    try:
        b.decode("utf-8"); print("  UTF-8 可解 -> 可能是 UTF-8")
    except UnicodeDecodeError:
        print("  UTF-8 不可解 -> 确认是 GBK/ANSI 编码 OK")
    print()
