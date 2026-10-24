import os, hashlib, sys
sys.path.insert(0, r"F:\sr2-cn")
from _vpp import Vpp

GAME = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
targets = ("vint_proj", "vint_doc", "vf3", "charlist")
hits = {}
for root, dirs, files in os.walk(GAME):
    for f in files:
        if not f.lower().endswith((".vpp_pc", ".vpp")):
            continue
        p = os.path.join(root, f)
        try:
            v = Vpp(p)
            ents = v.entries()
        except Exception as ex:
            print("SKIP", p, ex); continue
        for e in ents:
            nm = e["name"]; ex2 = e["ext"]
            if nm.startswith("sr2") and ex2 in ("vint_proj",):
                b = v.read(e)
                h = hashlib.md5(b).hexdigest()[:12]
                print("PROJ %-40s %s size=%d md5=%s" % (f, nm + "." + ex2, len(b), h))
                hits.setdefault(h, []).append(p + "::" + nm + "." + ex2)
            if ex2 == "vf3_pc" or ex2 == "vf3":
                print("VF3  %-40s %s size=%d" % (f, nm + "." + ex2, e["size"]))
            if nm.startswith("charlist"):
                b = v.read(e)
                h = hashlib.md5(b).hexdigest()[:12]
                print("CHAR %-40s %s size=%d md5=%s" % (f, nm + "." + ex2, len(b), h))
print("\n=== 重复 sr2.vint_proj ===")
for h, lst in hits.items():
    print(h, len(lst))
    for x in lst: print("   ", x)
