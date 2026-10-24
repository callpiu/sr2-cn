# -*- coding: utf-8 -*-
"""GH2: 把 hud_msg 的字体从 thin_overlay 改成 fnt_chinese（默认字体，面板证明可用）。

同时改两处：
  1) 松散覆盖文件 G:\\...\\Mods\\hud_msg.lua
  2) 各 VPP 内的 hud_msg.lua 副本
"""
import sys, os, glob, hashlib
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
OLD = b'vint_set_property(o, "font", "thin_overlay")'
NEW = b'vint_set_property(o, "font", "fnt_chinese")'
assert len(OLD) == len(NEW), (len(OLD), len(NEW))
print("等长替换 %d -> %d 字节" % (len(OLD), len(NEW)))

# ---- 1) 松散文件 ----
lp = os.path.join(G, "Mods", "hud_msg.lua")
b = open(lp, "rb").read()
n = b.count(OLD)
print("\n[松散] %s  出现 %d 次" % (lp, n))
if n:
    open(lp, "wb").write(b.replace(OLD, NEW))
    print("  已改 ->", lp)

# ---- 2) VPP 内副本 ----
for vp in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    try:
        v = Vpp(vp)
    except Exception as ex:
        print("[%s] 打开失败 %s" % (os.path.basename(vp), ex)); continue
    for e in v.entries():
        nm = (e["name"] or "")
        if nm != "hud_msg":
            continue
        raw = v.read(e)
        if OLD not in raw:
            print("[%s] hud_msg.%s (%d B) 无目标串" % (os.path.basename(vp), e["ext"], len(raw)))
            continue
        k = raw.count(OLD)
        v.replace_body_appended(e, raw.replace(OLD, NEW))
        v.save(vp)
        print("[%s] hud_msg.%s (%d B) 替换 %d 处 -> 已保存" % (os.path.basename(vp), e["ext"], len(raw), k))

# ---- 校验 ----
print("\n=== 校验 ===")
b = open(lp, "rb").read()
print("松散:", b.count(NEW), "处新串 /", b.count(OLD), "处旧串")
for vp in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    try:
        v = Vpp(vp)
    except Exception:
        continue
    for e in v.entries():
        if (e["name"] or "") == "hud_msg":
            raw = v.read(e)
            print("%s hud_msg.%s: 新串 %d 处, 旧串 %d 处" % (os.path.basename(vp), e["ext"], raw.count(NEW), raw.count(OLD)))
