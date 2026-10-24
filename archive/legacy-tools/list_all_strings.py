# -*- coding: utf-8 -*-
"""列出所有 VPP 容器内全部 le_strings 条目名 + 尺寸 + 首条解码文本。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SKIP = {"crashdumps", "__pycache__"}
vmain = Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in
       vmain.read(vmain.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]


def dec(slots):
    out = []
    for s in slots:
        i = s - 0x20
        out.append(chr(cps[i]) if 0 <= i < len(cps) else None)
    return None if any(c is None for c in out) else "".join(out)


for root, dirs, fs in os.walk(G):
    dirs[:] = [d for d in dirs if d.lower() not in SKIP]
    for f in sorted(fs):
        if not f.lower().endswith((".vpp_pc", ".vpp")):
            continue
        p = os.path.join(root, f)
        rel = os.path.relpath(p, G)
        if "before_" in rel or rel.endswith(".v42bak"):
            continue
        try:
            vv = Vpp(p)
            ents = [e for e in vv.entries() if e["ext"] == "le_strings"]
        except Exception:
            continue
        if not ents:
            continue
        print("== %s  (%d 个 le_strings)" % (rel, len(ents)))
        for en in ents:
            nm = en["name"]
            try:
                d = bytes(vv.read(vv.find(nm, "le_strings")))
                b, c, off_at, offs = file_offsets(d)
                r = read_units(d, offs[0] + 8)
                s0 = dec([x for x, _ in r[0]]) if r and r[0] else None
                ok = sum(1 for o in offs
                         if (lambda rr: rr and rr[0] and
                             dec([x for x, _ in rr[0]]) is not None)(read_units(d, o + 8)))
                print("    %-26s %8d B  可解码 %5d/%-5d  首条=%r"
                      % (nm, len(d), ok, len(offs), (s0 or "")[:26]))
            except Exception as e:
                print("    %-26s  ERR %s" % (nm, e))