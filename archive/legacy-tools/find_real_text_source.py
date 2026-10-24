# -*- coding: utf-8 -*-
"""找出游戏【真正加载】的文本与字体来源。

推理
    patch.vpp_pc 里有「直升機突襲」，但面板显示「直升機攻擊」
    => 游戏从别处加载了文本

可能
    (a) 某个 VPP 里也有一份 static_CH（优先级更高）
    (b) 引擎有内嵌文本
    (c) 有缓存文件

本脚本
    1. 遍历【所有】VPP，找 static_CH / charlist_CH 的所有副本
    2. 比较各副本，看哪个含「直升機攻擊」
    3. 找所有含 le_strings 扩展名的条目
"""
import os, sys, struct, hashlib

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

# 目标字节序列：「直升機攻擊」的槽位形式
sys.path.insert(0, r"F:\sr2-cn\pylibs")
from sr2lib import Vpp

v = Vpp(os.path.join(G, "patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
IDX = {chr(cp): i for i, cp in enumerate(cn)}


def seq(s):
    try:
        return b"".join(struct.pack(">H", IDX[c] + 0x20) for c in s)
    except KeyError:
        return None


PAT = {}
for w in ("直升機攻擊", "直升機突襲", "兄弟們", "正要去進行交易", "需要你的保護"):
    q = seq(w)
    if q:
        PAT[w] = q
print("目标模式:")
for w, q in PAT.items():
    print("  %-16s %s" % (w, q.hex(" ")))
print()

print("=== 遍历所有 VPP 的所有条目，找含这些模式的 ===")
for fn in sorted(os.listdir(G)):
    if not fn.lower().endswith(".vpp_pc"):
        continue
    p = os.path.join(G, fn)
    try:
        with LightVpp(p) as vv:
            for e in vv.entries():
                sz = e["size"]
                if sz < 16 or sz > 20 * 1024 * 1024:
                    continue
                try:
                    d = vv.read(e)
                except Exception:
                    continue
                for w, q in PAT.items():
                    i = d.find(q)
                    if i >= 0:
                        nm = vv.name(e)
                        ex = vv.ext(e)
                        print("  ★ %-16s #%-6d %-24s %-10s @0x%X  (%s)" %
                              (fn, e["idx"], nm, ex or "-", i, w))
                        break
    except Exception as ex:
        print("  %-18s 打不开: %s" % (fn, ex))
print()

# 所有 le_strings 条目
print("=== 所有 VPP 里的 le_strings 条目 ===")
for fn in sorted(os.listdir(G)):
    if not fn.lower().endswith(".vpp_pc"):
        continue
    p = os.path.join(G, fn)
    try:
        with LightVpp(p) as vv:
            ls = [(vv.name(e), vv.ext(e), e["size"]) for e in vv.entries()
                  if vv.ext(e) == "le_strings"]
            if ls:
                print("  %s: %d 个" % (fn, len(ls)))
                for nm, ex, sz in sorted(ls):
                    print("      %-26s %8d" % (nm, sz))
    except Exception:
        pass
