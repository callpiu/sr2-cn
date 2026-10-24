# -*- coding: utf-8 -*-
"""在全部 VPP 容器 + 全部 loose le_strings 中定位目标词条。
   每条记录都用【该资源自己的字表】解码 —— 英文表/日文表必须用自己的表。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
SKIP = {"crashdumps", "__pycache__"}

v = Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in
       v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]


def dec(slots, table):
    out = []
    for s in slots:
        idx = s - 0x20
        out.append(chr(table[idx]) if 0 <= idx < len(table) else None)
    return None if any(c is None for c in out) else "".join(out)


TARGETS = ("辩护律师", "三王", "丈王", "辩护")
found = []

def scan(name, d, table):
    try:
        b, c, off_at, offs = file_offsets(d)
    except Exception:
        return
    for off in offs:
        r = read_units(d, off + 8)
        if not r or not r[0]:
            continue
        slots = [x for x, _ in r[0]]
        t = dec(slots, table)
        if t is None:
            continue
        for tg in TARGETS:
            if tg in t:
                found.append((name, off, tg, t, slots))
                print("  ★ %-46s @%-8d [%s] %r" % (name, off, tg, t))
                break


print("### A. VPP 容器内的 le_strings（用 CH 字表解码）")
for root, dirs, fs in os.walk(G):
    dirs[:] = [d for d in dirs if d.lower() not in SKIP]
    for f in fs:
        if not f.lower().endswith((".vpp_pc", ".vpp")):
            continue
        p = os.path.join(root, f)
        rel = os.path.relpath(p, G)
        if "before_" in rel or rel.endswith(".v42bak"):
            continue
        try:
            vv = Vpp(p)
            for en in vv.entries():
                if en["ext"] != "le_strings":
                    continue
                nm = en["name"]
                # 只用 CH 表解 CH 文件；英/日文件跳过（日表命中是噪声）
                if not nm.endswith("CH") and nm != "static":
                    continue
                scan("%s:%s" % (rel, nm), bytes(vv.read(vv.find(nm, "le_strings"))), cps)
        except Exception:
            pass

print("\n### B. loose le_strings 文件")
for root, dirs, fs in os.walk(G):
    dirs[:] = [d for d in dirs if d.lower() not in SKIP]
    for f in fs:
        if not f.endswith(".le_strings"):
            continue
        p = os.path.join(root, f)
        rel = os.path.relpath(p, G)
        if "ch" not in f.lower():
            continue
        scan("loose:" + rel, open(p, "rb").read(), cps)

print("\n### 汇总 %d 条" % len(found))
for nm, off, tg, t, slots in found:
    print("  %-46s @%-8d 目标=%-6s slots=%s" % (nm, off, tg, slots))