import os, struct
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
H1, H2 = 0x84F287ED, 0x10AF1E62
pats = {}
for h in (H1, H2):
    pats["0x%08X" % h] = [struct.pack("<I", h), struct.pack(">I", h)]
files = ["SR2_pc.exe", "DFEngine.dll", "sr2_pc_unpatched.exe", "SR2_pc.exe.bak", "binkw32.dll", "SDL3.dll"]
print("=== 在 exe / DLL 里搜 hash ===")
for fn in files:
    p = os.path.join(G, fn)
    if not os.path.exists(p): 
        print("  %-24s 不存在" % fn); continue
    d = open(p,"rb").read()
    found = []
    for name, ps in pats.items():
        for q in ps:
            i = d.find(q)
            if i >= 0:
                found.append("%s@0x%X" % (name, i))
    print("  %-24s %s" % (fn, ", ".join(found) if found else "未找到"))
print()
# achievements.xtbl / 相关文本
print("=== 搜活动名「直升机突击」的槽位序列（在 patch 内所有条目）===")
import sys
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
v = Vpp(os.path.join(G,"patch.vpp_pc"))
cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
IDX = {chr(cp): i for i,cp in enumerate(cn)}
def slotseq(s):
    try: return b"".join(struct.pack(">H", IDX[c]+0x20) for c in s)
    except KeyError: return None
for w in ("直升机突击","突击","停靠","面包车耐久"):
    q = slotseq(w)
    if not q: print("  %-10s 构造失败" % w); continue
    hit = []
    for e in v.entries():
        try: d = bytes(v.read(e))
        except Exception: continue
        if q in d: hit.append("%s.%s" % (e["name"], e["ext"] or "-"))
    print("  %-10s -> %s" % (w, ", ".join(hit[:6]) if hit else "未找到"))
