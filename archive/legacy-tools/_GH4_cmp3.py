# -*- coding: utf-8 -*-
"""GH4: 对比 官方原版 / 最初汉化 / 当前 三份 patch.vpp_pc 里的 hud_msg.lua 字体行。"""
import sys, os, hashlib
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

CANDS = [
    ("官方原版 pristine", r"F:\sr2-cn\pristine\patch.vpp_pc"),
    ("最初汉化 _zip92", r"F:\sr2-cn\_zip92\黑道圣徒2简体汉化补丁\patch.vpp_pc"),
    ("游戏当前", r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc"),
]

def md5f(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

for label, p in CANDS:
    if not os.path.exists(p):
        print("\n[%s] 不存在: %s" % (label, p)); continue
    print("\n===== %s  (%d B, md5 %s) =====" % (label, os.path.getsize(p), md5f(p)[:12]))
    try:
        v = Vpp(p)
    except Exception as ex:
        print("  打开失败:", ex); continue
    found = False
    for e in v.entries():
        if (e["name"] or "") == "hud_msg":
            raw = v.read(e)
            found = True
            print("  hud_msg.%s  %d B" % (e["ext"], len(raw)))
            if e["ext"] == "lua":
                for i, ln in enumerate(raw.decode("utf-8", "replace").splitlines(), 1):
                    if "font" in ln and ("thin" in ln or "fnt_" in ln):
                        print("     %d | %s" % (i, ln.strip()))
                for key in (b'"thin_overlay"', b'"thin"', b'"fnt_chinese"', b'"fnt_body_n"'):
                    if key in raw:
                        print("     含 %s : %d 处" % (key.decode(), raw.count(key)))
    if not found:
        print("  无 hud_msg 条目")
