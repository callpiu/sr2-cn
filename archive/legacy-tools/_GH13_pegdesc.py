# -*- coding: utf-8 -*-
import sys, os, struct, re
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "pegs.vpp_pc"))
for e in v.entries():
    nm = (e["name"] or "")
    if not nm.startswith("fnt_"):
        continue
    raw = v.read(e)
    strs = [m.group().decode("ascii") for m in re.finditer(rb"[\x20-\x7e]{3,}", raw)]
    print("\n== %s (idx=%s, %d B) ==" % (nm, e["idx"], len(raw)))
    print("   hex:", " ".join("%02X" % c for c in raw[:40]))
    print("   串 :", strs)
    if len(raw) >= 0x38:
        print("   @8=%d @0x0C=%d @0x10=0x%X @0x14=0x%X @0x18=0x%X @0x1C=0x%X @0x20=0x%X @0x34=%d" % (
            struct.unpack_from("<I", raw, 8)[0], struct.unpack_from("<I", raw, 0x0C)[0],
            struct.unpack_from("<I", raw, 0x10)[0], struct.unpack_from("<I", raw, 0x14)[0],
            struct.unpack_from("<I", raw, 0x18)[0], struct.unpack_from("<I", raw, 0x1C)[0],
            struct.unpack_from("<I", raw, 0x20)[0], struct.unpack_from("<I", raw, 0x34)[0]))
