import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
def slot(ch): return CPS.index(ord(ch))+0x20
pats = {}
for w in ("三王","丈王","三","王","三王帮","三合会"):
    if all(ord(c) in CPS for c in w):
        pats[w] = b"".join(struct.pack("<H", slot(c)) for c in w)
print("目标字节序列:")
for w,p in pats.items():
    print("  %-8s -> %s" % (w, p.hex(" ")))
print()
print("=== 全资源字节搜索 ===")
for e in v.entries():
    if e["size"] > 6_000_000: continue
    try: d = bytes(v.read(e))
    except Exception: continue
    for w,p in pats.items():
        if w in ("三","王"): continue
        if p in d:
            print("  %-30s %-10s 命中 %s @0x%X" % (e["name"], e["ext"] or "-", w, d.find(p)))
