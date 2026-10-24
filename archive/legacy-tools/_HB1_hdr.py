import os, sys, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
for nm in ["static_CH", "hud_text"]:
    e = v.find(nm)
    if not e:
        print(nm, "MISSING"); continue
    d = v.read(e)
    print(f"=== {nm} size={len(d)}")
    for off in range(0, 64, 16):
        print(f"  {off:04x}  " + " ".join(f"{b:02x}" for b in d[off:off+16]))
    magic, ver, b1, cnt = struct.unpack_from('<IHHI', d, 0)
    print(f"  magic={magic:#x} u16@4={ver:#x} u16@6={b1} u32@8={cnt} u32@12={struct.unpack_from('<I',d,12)[0]}")
