import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
sl = lambda ch: CPS.index(ord(ch))+0x20
P_SAN = struct.pack("<HH", sl("三"), sl("王"))
P_ZHANG = struct.pack("<HH", sl("丈"), sl("王"))
print("三王=%s  丈王=%s" % (P_SAN.hex(" "), P_ZHANG.hex(" ")))
print()
print("=== 松散文件 ===")
for root, dirs, fs in os.walk(G):
    if "_archive" in root: continue
    for f in fs:
        p = os.path.join(root,f)
        try:
            if os.path.getsize(p) > 30*1024*1024: continue
            d = open(p,"rb").read()
        except Exception: continue
        for tag, pat in (("三王",P_SAN),("丈王",P_ZHANG)):
            if pat in d:
                print("  %-58s %s @0x%X" % (os.path.relpath(p,G), tag, d.find(pat)))
print()
print("=== patch.vpp_pc 所有条目 ===")
for e in v.entries():
    try: d = bytes(v.read(e))
    except Exception: continue
    for tag, pat in (("三王",P_SAN),("丈王",P_ZHANG)):
        if pat in d:
            print("  %-30s %-10s %s @0x%X" % (e["name"], e["ext"] or "-", tag, d.find(pat)))
