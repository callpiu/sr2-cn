# -*- coding: utf-8 -*-
"""扫描 patch.vpp_pc 内所有 XML/文本表，找「三王」「丈王」「辩护」的真实出处。"""
import sys, os, re
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in
       v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
slot2ch = {i + 0x20: chr(c) for i, c in enumerate(cps)}

TARGETS = ["三王", "丈王", "辩护律师", "辩护", "三", "王"]

print("### 扫描所有资源（含非 le_strings）")
for en in sorted(v.entries(), key=lambda e: e["name"]):
    nm, ex, sz = en["name"], en["ext"], en["size"]
    if sz > 2_000_000 or sz == 0:
        continue
    try:
        d = bytes(v.read(v.find(nm, ex)))
    except Exception:
        continue

    # 情况1：直接是文本
    try:
        t = d.decode("utf-8")
        if "<" in t[:200] and t.count("<") > 5:
            hits = {w: t.count(w) for w in ("三王", "丈王", "辩护", "律师") if w in t}
            if any(hits.values()):
                print("\n★ 文本命中 %s.%s (%d B): %s" % (nm, ex, sz, hits))
                for w in hits:
                    for m in list(re.finditer(re.escape(w), t))[:4]:
                        s = max(0, m.start() - 150)
                        print("    [%s] ...%s..." % (
                            w, t[s:m.end() + 150].replace("\r", " ").replace("\n", " ")[:320]))
            continue
    except UnicodeDecodeError:
        pass

    # 情况2：槽位编码的le_strings
    if d[:4] == b"\x01\x56\x4E\xF3" or (len(d) > 16 and d[4:8] == b"\x02\x00\x00\x00"):
        try:
            from sr2patch import file_offsets, read_units
            b, c, off_at, offs = file_offsets(d)
        except Exception:
            continue
        for off in offs:
            r = read_units(d, off + 8)
            if not r or not r[0]:
                continue
            slots = [x for x, _ in r[0]]
            if any(s not in slot2ch and s >= 0x20 for s in slots):
                continue
            t = "".join(slot2ch.get(s, chr(s) if s < 0x20 else "?")
                        for s in slots)
            if any(w in t for w in ("三王", "丈王", "辩护", "律师")):
                print("\n★ 槽位命中 %s.%s @%d: %r  slots=%s"
                      % (nm, ex, off, t, slots))
print("\n完成")