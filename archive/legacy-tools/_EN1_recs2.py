import sys, os, struct
from collections import Counter
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def get(p,n,e):
    v=Vpp(p); return v.read(v.find(n,e))
for tag,p in (("mine", os.path.join(G,"patch.vpp_pc")),
              ("official", r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")):
    b = get(p,"fnt_chinese","vf3_pc")
    N = struct.unpack_from('<I',b,8)[0]
    R = [struct.unpack_from('<IIII', b, 0xBC+i*16) for i in range(N)]
    print("=== %s  N=%d ===" % (tag, N))
    print("   w: min=%d max=%d  h: min=%d max=%d" % (min(r[0] for r in R), max(r[0] for r in R), min(r[1] for r in R), max(r[1] for r in R)))
    print("   field2:", Counter(r[2] for r in R).most_common(3))
    print("   field3:", Counter(r[3] for r in R).most_common(3))
    for i in (0,33,224,371,1035):
        print("   rec[%d] = %s" % (i, R[i]))
