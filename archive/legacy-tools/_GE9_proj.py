# -*- coding: utf-8 -*-
"""GE9: dump 备份中原始 sr2.vint_proj 的完整 font_info 区域。"""
import sys, os, re
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

CAND = [
    ("before_fontfix(M)", r"F:\sr2-cn\_backup_M\common.vpp_pc.before_fontfix"),
    ("before_desc_fix(N)", r"F:\sr2-cn\_backup_N\common.vpp_pc.before_desc_fix"),
    ("CUR-game", r"G:\SteamLibrary\steamapps\common\Saints Row 2\common.vpp_pc"),
]

for tag, p in CAND:
    if not os.path.exists(p):
        print("[%s] MISSING %s" % (tag, p)); continue
    v = Vpp(p)
    e = v.find("sr2", "vint_proj")
    if not e:
        print("[%s] 无 sr2.vint_proj" % tag); continue
    raw = v.read(e)
    print("=" * 72)
    print("[%s] sr2.vint_proj  %d bytes" % (tag, len(raw)))
    txt = raw.decode("utf-8", "replace")
    i = txt.find("<font_info>")
    j = txt.rfind("</font_info>")
    if i < 0:
        print("  无 <font_info>; 片段:", txt[:300].replace("\n", " ")); continue
    blk = txt[i:j + 12]
    # 按 alias 分组打印
    for m in re.finditer(r"<font_info>(.*?)</font_info>", blk, re.S):
        b = m.group(1)
        g = lambda t: (re.search(r"<%s>\s*([^<\s]+)\s*</%s>" % (t, t), b) or [None, None])[1]
        print("   alias=%-20s filename=%-16s overlay=%s" % (g("alias"), g("filename"), g("filename_overlay")))
