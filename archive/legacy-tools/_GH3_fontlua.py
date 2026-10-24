# -*- coding: utf-8 -*-
"""GH3: 把真正被加载的 patch.vpp_pc/hud_msg.lua 里的字体 thin_overlay -> fnt_chinese。

依据：
  - debug.txt 的 [LOOSE_FILE] 列表里没有 mods\\hud_msg.lua => 松散文件不被加载
  - common.vpp_pc 只有 hud_msg.vint_doc（布局锚点，引用 hud_msg.lua）
  - hud_msg.lua 只存在于 patch.vpp_pc（7817 B，第 106 行）
  - [LOOSE_FILE] patch.vpp_pc => patch.vpp_pc 整体最高优先级
"""
import sys, os, shutil, hashlib
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
BAK = r"F:\sr2-cn\_backup_P"
os.makedirs(BAK, exist_ok=True)

OLD = b'vint_set_property(o, "font", "thin_overlay")'
NEW = b'vint_set_property(o, "font", "fnt_chinese")'
print("OLD %d B / NEW %d B (差 %d)" % (len(OLD), len(NEW), len(OLD) - len(NEW)))

def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

# ---------- 1) patch.vpp_pc ----------
pp = os.path.join(G, "patch.vpp_pc")
print("\npatch.vpp_pc 改前 md5:", md5f(pp), os.path.getsize(pp))
dst = os.path.join(BAK, "patch.vpp_pc.before_fontlua")
if not os.path.exists(dst):
    shutil.copy2(pp, dst); print("备份 ->", dst)

v = Vpp(pp)
done = False
for e in v.entries():
    if (e["name"] or "") == "hud_msg" and e["ext"] == "lua":
        raw = v.read(e)
        k = raw.count(OLD)
        print("patch/hud_msg.lua %d B  目标串 %d 处" % (len(raw), k))
        assert k == 1, k
        v.replace_body_appended(e, raw.replace(OLD, NEW))
        v.save(pp)
        done = True
print("patch.vpp_pc 已保存:", done)
print("patch.vpp_pc 改后 md5:", md5f(pp), os.path.getsize(pp))

# ---------- 2) 松散（保险，虽然不加载） ----------
lp = os.path.join(G, "Mods", "hud_msg.lua")
b = open(lp, "rb").read()
k = b.count(OLD)
print("\n松散 Mods/hud_msg.lua 目标串 %d 处" % k)
if k:
    open(lp, "wb").write(b.replace(OLD, NEW))
    print("  已改")

# ---------- 3) 校验 ----------
print("\n=== 校验 ===")
v2 = Vpp(pp)
for e in v2.entries():
    if (e["name"] or "") == "hud_msg" and e["ext"] == "lua":
        raw = v2.read(e)
        print("patch/hud_msg.lua: 新串 %d 处 / 旧串 %d 处" % (raw.count(NEW), raw.count(OLD)))
        t = raw.decode("utf-8", "replace").splitlines()
        for i, ln in enumerate(t, 1):
            if "font" in ln and "thin" in ln or "fnt_chinese" in ln:
                print("   %d | %s" % (i, ln.strip()))
b2 = open(lp, "rb").read()
print("松散: 新串 %d 处 / 旧串 %d 处" % (b2.count(NEW), b2.count(OLD)))
