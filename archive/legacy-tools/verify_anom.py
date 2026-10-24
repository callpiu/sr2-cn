import os, sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def anomalies(p):
    v = Vpp(p)
    d = bytes(v.read(v.find("static_CH","le_strings")))
    CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
    b,c,oa,offs = file_offsets(d)
    tot = 0; recs = []
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        u,_ = read_units(d, off+8)
        if u is None: continue
        t = "".join(S.get(x,"\uFFFD") for x,_ in u)
        n = t.count("\uFFFD")
        if n: tot += n; recs.append((off, n))
    return tot, recs, len(S)
for label, p in (("原始（汉化）", os.path.join(G,"patch.vpp_pc")),
                 ("修复A4",       r"F:\sr2-cn\_fix_candidates\patch_fixA4_noimg.vpp_pc")):
    tot, recs, ns = anomalies(p)
    print("=== %s ===" % label)
    print("  异常字符总数: %d" % tot)
    print("  涉及记录数: %d" % len(recs))
    print("  前 5 条: %s" % recs[:5])
    print()
