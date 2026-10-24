import sys, os, collections
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
def dec(vals): return "".join(S.get(x,"·") for x in vals)
# 检查 三/丈/律/延 是否在表里
for ch in "三丈律延王":
    print("  %s 在字表: %s (slot %s)" % (ch, ord(ch) in CPS, (CPS.index(ord(ch))+0x20) if ord(ch) in CPS else "-"))
print()
# 收集全部文本，统计「丈王」「三王」「延师」「律师」出现次数
allt = collections.Counter()
FILES = ("static_CH","voice_script_CH","platform_pc_CH")
recs = {}
for nm in FILES:
    e = v.find(nm,"le_strings")
    if not e: continue
    d = bytes(v.read(e))
    b,c,oa,offs = file_offsets(d)
    L = {}
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        u,_ = read_units(d, off+8)
        if u is None: continue
        L[off] = [x for x,_ in u]
    recs[nm] = L
    for vals in L.values():
        t = dec(vals)
        allt[t] += 1
joined = "\n".join(allt)
print("=== 目标词统计 ===")
for w in ("丈王","三王","延师","律师","丈","三王","辩护","辩","护"):
    print("  %-6s 出现 %d 次" % (w, joined.count(w)))
print()
# 列出所有含「丈王」的记录
print("=== 含「丈王」的记录 ===")
n=0
for nm, L in recs.items():
    for off, vals in L.items():
        t = dec(vals)
        if "丈王" in t:
            print("  %-16s @%-8d %s" % (nm, off, t[:50]))
            n += 1
            if n >= 10: break
    if n >= 10: break
print()
print("=== 含「延师」的记录 ===")
n=0
for nm, L in recs.items():
    for off, vals in L.items():
        t = dec(vals)
        if "延师" in t:
            print("  %-16s @%-8d %s" % (nm, off, t[:50]))
            n += 1
            if n >= 10: break
    if n >= 10: break
if n==0: print("  （没找到「延师」，可能字形确实不同）")
