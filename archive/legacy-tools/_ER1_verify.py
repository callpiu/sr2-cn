import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load_charlist(path, name="charlist_CH"):
    v = Vpp(path)
    e = v.find(name, "txt")
    if e is None:
        return None
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = load_charlist(os.path.join(G, "patch.vpp_pc"))
O = load_charlist(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")
print("M (current charlist) len =", len(M))
print("O (official charlist) len =", len(O))
print()

# on-screen sentence: "your brothers need your protection" (11 chars)
RIGHT = [0x4F60,0x7684,0x5F1F,0x5144,0x4EEC,0x9700,0x8981,0x4F60,0x7684,0x4FDD,0x62A4]
# what the user sees: "ren can ou qiao wei xiong heng ren can wei gai"
WRONG = [0x4EFB,0x74A8,0x5076,0x5DE7,0x4F4D,0x96C4,0x8861,0x4EFB,0x74A8,0x4F2A,0x8BE5]

print("=== mechanism test (per char) ===")
print("right  wrong   iM     iO     O[iM]   M[iO]   verdict")
for r, w in zip(RIGHT, WRONG):
    iM = M.index(r) if r in M else -1
    iO = O.index(r) if r in O else -1
    oim = O[iM] if 0 <= iM < len(O) else None
    mio = M[iO] if 0 <= iO < len(M) else None
    v = []
    if oim == w: v.append("O[iM]==WRONG")
    if mio == w: v.append("M[iO]==WRONG")
    print("%-6s %-6s %-6d %-6d %-7s %-7s %s" % (
        hex(r), hex(w), iM, iO,
        hex(oim) if oim is not None else "-",
        hex(mio) if mio is not None else "-",
        ",".join(v) or "-"))

print()
print("=== wrong chars membership ===")
for w in sorted(set(WRONG)):
    print("  U+%04X inM=%-5s inO=%-5s  Mi=%-5s Oi=%-5s" % (
        w, w in M, w in O,
        M.index(w) if w in M else "-", O.index(w) if w in O else "-"))

print()
print("=== iM vs iO relation ===")
for r in sorted(set(RIGHT)):
    if r in M and r in O:
        print("  U+%04X  iM=%4d  iO=%4d  diff=%d" % (r, M.index(r), O.index(r), O.index(r) - M.index(r)))

print()
print("=== sentence hunt ===")
SENT = RIGHT
enc = {
    "M_code+32": b"".join(struct.pack("<H", M.index(c) + 32) for c in SENT),
    "M_code+0":  b"".join(struct.pack("<H", M.index(c)) for c in SENT),
    "O_code+32": b"".join(struct.pack("<H", O.index(c) + 32) for c in SENT),
    "raw_unicode": b"".join(struct.pack("<H", c) for c in SENT),
}
for k, v in enc.items():
    print("  %-11s = %s" % (k, v.hex()))

targets = []
for f in ("patch.vpp_pc", "common.vpp_pc"):
    p = os.path.join(G, f)
    try:
        vp = Vpp(p)
        for e in vp.entries():
            if "string" in (e.get("ext") or ""):
                targets.append(("%s:%s.%s" % (f, e["name"], e.get("ext")), vp.read(e)))
    except Exception as ex:
        print("  ERR", f, ex)
for dp, _, fns in os.walk(os.path.join(G, "Mods")):
    for fn in fns:
        if fn.lower().endswith(".le_strings"):
            fp = os.path.join(dp, fn)
            targets.append(("LOOSE:" + fn, open(fp, "rb").read()))

print("  scanned files:", len(targets))
for tag, b in targets:
    for k, pat in enc.items():
        i = b.find(pat)
        if i >= 0:
            print("  [HIT %s] %s @%d" % (k, tag, i))
print("done")
