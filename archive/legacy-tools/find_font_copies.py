# -*- coding: utf-8 -*-
"""确认 fnt_body_n / fnt_body_s 的资源来源，并规划修复。

问题
    thin_overlay -> (fnt_body_n, fnt_body_s)，两者 N=224（仅 ASCII）
    => 字幕无法渲染 CJK

我上次改了 common.vpp_pc 的 fnt_body_n.vf3_pc（N=224 -> 2838）+ pegs 描述符
但字幕无变化 => 说明游戏读的不是我改的那份

本脚本
    1. 找出所有 VPP 里 fnt_body_n / fnt_body_s 的所有副本
    2. 比较各处副本的 md5，确认哪份被改过
    3. 打印 patch.vpp_pc 的完整条目列表（找 fnt_*）
"""
import os, sys, hashlib

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
TARGETS = ["fnt_body_n", "fnt_body_s", "fnt_chinese", "fnt_bodyital_n", "fnt_head_n"]

print("=== 所有 VPP 里 fnt_body_n / fnt_body_s 的副本 ===")
for fn in sorted(os.listdir(G)):
    if not fn.lower().endswith(".vpp_pc"):
        continue
    p = os.path.join(G, fn)
    try:
        with LightVpp(p) as v:
            for e in v.entries():
                nm = v.name(e)
                if nm in TARGETS:
                    d = v.read(e)
                    print("  %-18s #%-6d %-16s %-10s %8d  md5 %s" %
                          (fn, e["idx"], nm, v.ext(e) or "-", e["size"],
                           hashlib.md5(d).hexdigest()[:12]))
    except Exception as ex:
        print("  %-18s 打不开: %s" % (fn, ex))
print()

# 对照：备份里的原始版本
print("=== 备份里的同名条目（判断我改了什么）===")
B = r"F:\sr2-cn\_fontfix_backup"
for fn in ("common.vpp_pc", "pegs.vpp_pc"):
    p = os.path.join(B, fn)
    if not os.path.exists(p):
        print("  %s 备份不存在" % fn)
        continue
    try:
        with LightVpp(p) as v:
            for e in v.entries():
                nm = v.name(e)
                if nm in ("fnt_body_n", "fnt_body_s"):
                    d = v.read(e)
                    print("  [备份] %-14s %-16s %-10s %8d  md5 %s" %
                          (fn, nm, v.ext(e) or "-", e["size"], hashlib.md5(d).hexdigest()[:12]))
    except Exception as ex:
        print("  %s: %s" % (fn, ex))
print()

# patch.vpp_pc 完整列表（715 条，只看 font/text/pegs 相关）
print("=== patch.vpp_pc 里与字体/文本相关的条目 ===")
with LightVpp(os.path.join(G, "patch.vpp_pc")) as v:
    for e in v.entries():
        nm = v.name(e)
        ex = v.ext(e)
        if nm.startswith(("fnt_", "charlist", "static_", "platform_", "voice_")) or "font" in nm.lower():
            print("  #%-6d %-28s %-12s %8d" % (e["idx"], nm, ex or "-", e["size"]))
