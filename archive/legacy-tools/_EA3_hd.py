import sys, os
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
b = Vpp(os.path.join(G,"patch.vpp_pc")).read(Vpp(os.path.join(G,"patch.vpp_pc")).find("static_CH","le_strings"))
for off in range(0, 96, 16):
    row = b[off:off+16]
    print("%06x  %-47s  %s" % (off, " ".join("%02x"%c for c in row),
          "".join(chr(c) if 32<=c<127 else "." for c in row)))
