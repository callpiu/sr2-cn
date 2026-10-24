# -*- coding: utf-8 -*-
"""GH11: 路线A —— 把 patch.vpp_pc 内 hud_msg.lua / hud.lua 的字体改为 fnt_chinese。

理由：
  - debug.txt 的 [LOOSE_FILE] 列表不含 mods\\hud*.lua => 松散文件不加载
  - hud_msg.lua 只在 patch.vpp_pc 里 => patch 内那份才生效
  - 改 vint_proj / vf3 / 图集 / 描述符 全部实测无效 => 直接改 lua 字体名绕过别名解析
  - HUD 面板不设字体即用默认 fnt_chinese 且显示正常 => fnt_chinese 可用
"""
import sys, os, shutil, hashlib
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
BAK = r"F:\sr2-cn\_backup_P"
os.makedirs(BAK, exist_ok=True)

REPL = [
    (b'vint_set_property(o, "font", "thin_overlay")',
     b'vint_set_property(o, "font", "fnt_chinese")'),
    (b'vint_set_property(Hud_radial_menu.slot_desc_h, "font", "thin")',
     b'vint_set_property(Hud_radial_menu.slot_desc_h, "font", "fnt_chinese")'),
    (b'vint_set_property(Hud_radial_menu.slot_desc_h, "font", "thin_overlay")',
     b'vint_set_property(Hud_radial_menu.slot_desc_h, "font", "fnt_chinese")'),
]

def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

# ---------- patch.vpp_pc ----------
pp = os.path.join(G, "patch.vpp_pc")
print("patch.vpp_pc 改前: %d B  md5 %s" % (os.path.getsize(pp), md5f(pp)))
dst = os.path.join(BAK, "patch.vpp_pc.before_luafont")
if not os.path.exists(dst):
    shutil.copy2(pp, dst); print("备份 ->", dst)

v = Vpp(pp)
TARGET_LUA = {"hud_msg", "hud"}
for e in v.entries():
    nm = (e["name"] or "")
    if nm not in TARGET_LUA or e["ext"] != "lua":
        continue
    raw = v.read(e)
    new = raw
    n = 0
    for old, rep in REPL:
        c = new.count(old)
        if c:
            new = new.replace(old, rep)
            n += c
    if n:
        v.replace_body_appended(e, new)
        print("  %s.lua %d B: 替换 %d 处" % (nm, len(raw), n))
v.save(pp)
print("patch.vpp_pc 改后: %d B  md5 %s" % (os.path.getsize(pp), md5f(pp)))

# ---------- 松散文件（保险） ----------
for fn in ("hud_msg.lua", "hud.lua"):
    lp = os.path.join(G, "Mods", fn)
    if not os.path.exists(lp):
        continue
    b = open(lp, "rb").read()
    nb = b
    n = 0
    for old, rep in REPL:
        c = nb.count(old)
        if c:
            nb = nb.replace(old, rep); n += c
    if n:
        open(lp, "wb").write(nb)
        print("  松散 %s: 替换 %d 处" % (fn, n))

# ---------- 校验 ----------
print("\n=== 校验 patch.vpp_pc ===")
v2 = Vpp(pp)
for e in v2.entries():
    nm = (e["name"] or "")
    if nm in TARGET_LUA and e["ext"] == "lua":
        raw = v2.read(e)
        print("  %s.lua: fnt_chinese %d 处 / thin_overlay %d 处" % (
            nm, raw.count(b'"fnt_chinese"'), raw.count(b'"thin_overlay"')))
        for i, ln in enumerate(raw.decode("utf-8", "replace").splitlines(), 1):
            if "font" in ln and "fnt_chinese" in ln:
                print("     %d | %s" % (i, ln.strip()))
