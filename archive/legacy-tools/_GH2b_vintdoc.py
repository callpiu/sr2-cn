# -*- coding: utf-8 -*-
"""GH2b: dump common.vpp_pc 里的 hud_msg.vint_doc 全文，搜字体名。"""
import sys, os, glob, re
sys.path.insert(0, r"F:\sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def dump(buf, label):
    print("\n===== %s  %d B =====" % (label, len(buf)))
    # 提取可打印 ASCII 串（>=4）
    for m in re.finditer(rb"[\x20-\x7e]{4,}", buf):
        s = m.group().decode("ascii")
        if any(k in s for k in ("font", "thin", "fnt", "vint", "overlay", "body", "head", "chinese", "hud", "msg")):
            print("  @%06X  %s" % (m.start(), s))

vp = os.path.join(G, "common.vpp_pc")
v = Vpp(vp)
for e in v.entries():
    if (e["name"] or "") == "hud_msg" and e["ext"] == "vint_doc":
        raw = v.read(e)
        dump(raw, "common/hud_msg.vint_doc")
        # 全部可打印串
        print("  --- 全部可打印串 ---")
        for m in re.finditer(rb"[\x20-\x7e]{3,}", raw):
            print("    @%06X  %s" % (m.start(), m.group().decode("ascii")))
        # 找字体名相关字节
        for key in (b"thin", b"fnt", b"font", b"body", b"head", b"chinese", b"overlay"):
            for m in re.finditer(re.escape(key), raw):
                print("    [%s] @%06X" % (key.decode(), m.start()))
