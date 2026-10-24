# -*- coding: utf-8 -*-
"""GI1: 回退 lua 字体改动（fnt_chinese -> thin_overlay/thin），保留 exe 改名。

结论依据：用户实测「所有字幕都不见了」=> lua 修改确实生效，
但 font 属性只接受别名(thin/thin_overlay)，不接受字体资源名(fnt_chinese)。
所以正确做法 = lua 保持 thin_overlay，改由 exe 字体名表把英文字体指向 fnt_chinese。
"""
import sys, os, shutil, hashlib
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

# ---- 1) patch.vpp_pc 直接还原到改 lua 之前 ----
src = r"F:\sr2-cn\_backup_P\patch.vpp_pc.before_luafont"
dst = os.path.join(G, "patch.vpp_pc")
print("patch 改前:", os.path.getsize(dst), md5f(dst))
shutil.copy2(src, dst)
print("patch 还原:", os.path.getsize(dst), md5f(dst))

# ---- 2) 松散文件按行号改回 ----
NEW = b'"fnt_chinese"'
for fn, plan in (("hud_msg.lua", [(106, b'"thin_overlay"')]),
                 ("hud.lua",     [(2200, b'"thin"'), (2204, b'"thin_overlay"')])):
    lp = os.path.join(G, "Mods", fn)
    if not os.path.exists(lp):
        print("松散不存在:", fn); continue
    lines = open(lp, "rb").read().split(b"\n")
    for ln, val in plan:
        i = ln - 1
        if i < len(lines) and NEW in lines[i]:
            lines[i] = lines[i].replace(NEW, val)
            print("  %s 第%d行 -> %s" % (fn, ln, val.decode()))
        else:
            print("  %s 第%d行 无 %s" % (fn, ln, NEW.decode()))
    open(lp, "wb").write(b"\n".join(lines))

# ---- 3) 校验 ----
print("\n=== 校验 ===")
from sr2lib import Vpp
v = Vpp(dst)
for e in v.entries():
    nm = e["name"] or ""
    if nm in ("hud_msg", "hud") and e["ext"] == "lua":
        raw = v.read(e)
        print("  patch/%s.lua: thin_overlay %d 处 / fnt_chinese %d 处" % (
            nm, raw.count(b'"thin_overlay"'), raw.count(b'"fnt_chinese"')))
        for i, l in enumerate(raw.decode("utf-8", "replace").splitlines(), 1):
            if '"font"' in l:
                print("     %d | %s" % (i, l.strip()))
# exe 保持改名状态
exe = os.path.join(G, "SR2_pc.exe")
d = open(exe, "rb").read()
print("\nexe md5:", md5f(exe))
print("exe @10358780:", d[10358780:10358792].split(b"\x00")[0].decode())
