import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def get(p):
    v=Vpp(p); return v.read(v.find("static_CH","le_strings"))
A = get(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")   # 官方原版
B = get(os.path.join(G,"patch.vpp_pc"))              # 当前
for tag,x in (("官方",A),("当前",B)):
    n = struct.unpack_from('<I', x, 8)[0]
    lang = struct.unpack_from('<I', x, 12)[0]
    dirend = 16 + n*8
    print("=== %s: %d 字节, n=%d, lang=%d, dirend=%d ===" % (tag, len(x), n, lang, dirend))
    for off in (dirend, dirend+1):
        seg = x[off:off+96]
        t = seg.decode('utf-16-le','replace')
        print("  @+%-4d UTF16: %r" % (off-dirend, t[:48]))
        print("        hex : %s" % seg[:48].hex())
