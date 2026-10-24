import os, re
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
M = os.path.join(G,"Mods")
# 找菜单系统文件
cands = [f for f in os.listdir(M) if f.endswith(".lua")]
print("Mods 下的 lua 文件数: %d" % len(cands))
print()
# 找定义 label 解析的地方
for f in ("menu_base.lua","pause_menu.lua","sui_main_menu.lua","main_menu.lua"):
    p = os.path.join(M,f)
    if not os.path.exists(p): continue
    s = open(p, encoding="gbk", errors="replace").read()
    hits = []
    for pat in (r'get_localized_string', r'localize', r'locale', r'string_table', r'GetString',
                r'text_get', r'ui_get_string', r'resolve', r'label\s*\)', r'\.label'):
        for m in re.finditer(pat, s):
            ln = s[:m.start()].count("\n")+1
            hits.append((ln, pat, s.split("\n")[ln-1].strip()[:100]))
    seen=set()
    print("=== %s ===" % f)
    for ln, pat, line in hits[:14]:
        if (ln,pat) in seen: continue
        seen.add((ln,pat))
        print("  L%-6d [%s] %s" % (ln, pat, line))
    print()
