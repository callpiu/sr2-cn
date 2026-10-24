"""FX3: dump the peg descriptors for fnt_body_n / fnt_body_s / fnt_chinese /
fnt_korea, and resolve the atlas texture they reference.
"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
p = Vpp(os.path.join(G, "pegs.vpp_pc"))

for nm in ("fnt_body_n", "fnt_body_s", "fnt_chinese", "fnt_korea", "fnt_head_n", "fnt_bodyital_n"):
    e = p.find(nm)
    if e is None:
        print(nm, "MISSING"); continue
    d = p.read(e)
    print("=" * 60)
    print("%s  size=%d" % (nm, len(d)))
    print("  hex:", d.hex())
    print("  ascii:", "".join(chr(b) if 32 <= b < 127 else "." for b in d))
    if len(d) >= 32:
        print("  f0..f11:", struct.unpack_from("<III", d, 0))
        print("  dataSize@12:", struct.unpack_from("<I", d, 12)[0])
        print("  @20..: ", struct.unpack_from("<IIII", d, 20))
        print("  w,h @28:", struct.unpack_from("<HH", d, 28))
        print("  fmt @32:", struct.unpack_from("<I", d, 32)[0])
        print("  name @36:", d[36:].rstrip(b"\x00"))
