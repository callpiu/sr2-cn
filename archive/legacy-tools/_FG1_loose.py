import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = cl(os.path.join(G, "patch.vpp_pc"), "charlist_CH")
O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "charlist_CH")

def render(b, T):
    try:
        n = struct.unpack_from("<I", b, 8)[0]
    except Exception:
        return []
    if not (0 < n < 500000):
        return []
    start = 16 + n * 8
    if start >= len(b):
        return []
    nc = (len(b) - start) // 2
    codes = struct.unpack_from(">%dH" % nc, b, start)
    out = []; cur = []
    for c in codes:
        if c == 0:
            out.append("".join(cur)); cur = []
        elif c < 32:
            cur.append("")
        elif c - 32 < len(T):
            cur.append(chr(T[c - 32]))
        else:
            cur.append("~")
    return out

KEY1 = "".join(chr(c) for c in [0x9700, 0x8981, 0x4F60, 0x7684, 0x4FDD, 0x62A4])
KEY2 = "".join(chr(c) for c in [0x8981, 0x51FA, 0x53BB, 0x8C08, 0x51E0, 0x7B14, 0x751F, 0x610F])

files = [
    r"Mods\JUICED - Strings\patch_ch.le_strings",
    r"Mods\JUICED - Strings\juiced_CH.le_strings",
    r"Mods\static_US.le_strings",
    r"Mods\platform_PC_US.le_strings",
]
for rel in files:
    p = os.path.join(G, rel)
    if not os.path.exists(p):
        print("MISS", rel); continue
    b = open(p, "rb").read()
    print("=== %s  %d bytes  head=%s" % (rel, len(b), b[:24].hex()))
    for tag, T in (("M", M), ("O", O)):
        ps = render(b, T)
        nz = [x for x in ps if len(x) > 3]
        print("   [%s] pieces=%d" % (tag, len(ps)))
        if nz:
            print("       sample: %s" % " | ".join(nz[:4]))
        for s in ps:
            if KEY1 in s or KEY2 in s:
                print("       *** HIT(%s): %s" % (tag, s[:130]))
    print()
