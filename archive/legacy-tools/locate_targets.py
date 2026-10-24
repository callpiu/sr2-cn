# -*- coding: utf-8 -*-
"""精确定位「辩护律师」和「三王」所在条目的 resID。
   scan() 直接顺序扫记录区，不依赖哈希桶（与 v404 脚本同口径）。"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
import sr2lib
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = sr2lib.Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(x) for x in v.read(v.find("charlist_CH")).decode("utf-8").split("\n")
       if x.strip().isdigit()]
N = len(cps)
slot_of = {cp: i + 0x20 for i, cp in enumerate(cps)}


def scan(blob):
    """与 v404 脚本完全相同的扫描口径。"""
    bk = struct.unpack_from("<I", blob, 8)[0]
    ct = struct.unpack_from("<I", blob, 12)[0]
    o, e2, out = 16 + bk * 8 + ct * 4 + 4, len(blob), []
    while o < e2 - 1:
        st = o; sl = []
        while True:
            if o >= e2:
                return out
            s = struct.unpack_from(">H", blob, o)[0]; o += 2
            if s == 0:
                break
            sl.append(s)
        if sl:
            out.append((st, sl))
    return out


def dec(sl):
    out = []
    for s in sl:
        i = s - 0x20
        if 0 <= i < N:
            out.append(chr(cps[i]))
        elif s < 0x20:
            out.append({10: "\\n", 13: "\\r", 9: "\\t"}.get(s, "<c%d>" % s))
        else:
            out.append("<OOB:%d>" % s)
    return "".join(out)


for table in ("static_CH", "voice_script_CH"):
    blob = v.read(v.find(table))
    recs = scan(blob)
    print("=== %s  %d 字节  %d 条 ===" % (table, len(blob), len(recs)))

    # 1) 精确匹配目标文本
    for kw in ("辩护律师", "三王", "丈王"):
        hits = [(st, sl) for st, sl in recs
                if dec(sl[2:]) == kw or dec(sl[2:]).strip() == kw]
        print("  精确 %-6s : %d 条  %s"
              % (kw, len(hits), [(st, tuple(sl[:2])) for st, sl in hits]))

    # 2) 包含匹配
    for kw in ("辩护", "三王"):
        hits = [(st, sl) for st, sl in recs if kw in dec(sl[2:])]
        print("  包含 %-6s : %d 条" % (kw, len(hits)))
        for st, sl in hits:
            print("     @%-8d resID=%s  %r  slots=%s"
                  % (st, tuple(sl[:2]), dec(sl[2:])[:50], sl[2:10]))
    print()

# 3) 与「三街圣徒」先例对照：那条被改成 3rdS 的条目现在是什么
print("=== 对照：v404 改过的条目 resID=(29444,25978) ===")
blob = v.read(v.find("static_CH"))
for st, sl in scan(blob):
    if len(sl) >= 2 and tuple(sl[:2]) == (29444, 25978):
        print("  @%-8d 现译=%r slots=%s" % (st, dec(sl[2:]), sl[2:]))