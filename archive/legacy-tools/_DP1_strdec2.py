import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
def get(p):
    v=Vpp(p); return v.read(v.find("static_CH","le_strings"))
a=get(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig")
b=get(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
base = 12 + 12250*8
for tag,x in (("原始",a),("当前",b)):
    print("=== %s (base=%d) ===" % (tag, base))
    for off in (base, base+1, base-1):
        seg = x[off:off+400]
        t = seg.decode('utf-16-le','replace')
        print("  off=%d : %r" % (off, t[:60]))
    print()
