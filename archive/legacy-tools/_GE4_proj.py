# -*- coding: utf-8 -*-
"""GE4: 列出各 VPP 内所有 vint_proj, 并 dump 其 font_info 块。"""
import sys, os, re
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

ORIG = r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig"
HAN  = r"F:\sr2-cn\_zip92\黑道圣徒2简体汉化补丁\patch.vpp_pc"
G    = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def dump(tag, path):
    print("=" * 72)
    print("[%s] %s" % (tag, os.path.basename(path)))
    try:
        v = Vpp(path)
    except Exception as ex:
        print("  打开失败:", ex); return
    ents = v.entries()
    hits = []
    for k, e in enumerate(ents):
        nm = (e["name"] or "").lower()
        ex_ = (e["ext"] or "").lower()
        if "vint_proj" in nm or "vint_proj" in ex_ or nm.endswith(".vint_proj"):
            hits.append((k, e))
    print("  条目总数 %d, vint_proj 命中 %d" % (len(ents), len(hits)))
    for k, e in hits[:12]:
        raw = v.read(e)
        print("  #%d %s.%s  %d bytes" % (k, e["name"], e["ext"], len(raw)))
        try:
            txt = raw.decode("utf-8", "replace")
        except Exception:
            txt = raw.decode("latin-1", "replace")
        m = re.search(r"<font_info>.*?</font_info>", txt, re.S)
        if m:
            print("     font_info 长度 %d" % len(m.group(0)))
            for mm in re.finditer(r"<(alias|filename|filename_overlay)>\s*([^<\s]+)\s*</\1>", m.group(0)):
                print("       %-18s = %s" % (mm.group(1), mm.group(2)))
        else:
            i = txt.find("font_info")
            print("     无 <font_info> 块; 首次出现于 offset", i)

for tag, p in (("ORIG", ORIG), ("HAN", HAN),
               ("CUR-patch", os.path.join(G, "patch.vpp_pc")),
               ("CUR-common", os.path.join(G, "common.vpp_pc"))):
    dump(tag, p)
