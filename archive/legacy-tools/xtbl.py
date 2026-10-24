import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
for nm in ("Hoods","Gang_Names"):
    e = v.find(nm)
    d = bytes(v.read(e))
    print("=== %s (%d 字节) ===" % (nm, len(d)))
    print("  前 200 字节: %r" % d[:200])
    for enc in ("utf-8","utf-16-le","utf-16-be"):
        try:
            s = d.decode(enc)
            if "三" in s or "王" in s or "gang" in s.lower() or "hood" in s.lower():
                print("  %s 解码成功，长度 %d" % (enc, len(s)))
                print("  %s" % s[:600])
                break
        except Exception as ex:
            pass
    print()
