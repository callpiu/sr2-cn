"""FM2: where does '直升机突击' live, and how do the two broken strings decode
with M vs O?
"""
import sys, os, struct, glob
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = cl(os.path.join(G, "patch.vpp_pc"), "charlist_CH")
O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "charlist_CH")

def parse(b, T):
    n = struct.unpack_from("<I", b, 8)[0]
    start = 16 + n * 8
    nc = (len(b) - start) // 2
    codes = list(struct.unpack_from(">%dH" % nc, b, start))
    out = []; cur = []; st = 0
    for i, c in enumerate(codes):
        if c == 0:
            out.append((st, i, "".join(cur))); cur = []; st = i + 1
        elif c < 32:
            cur.append("")
        elif c - 32 < len(T):
            cur.append(chr(T[c - 32]))
        else:
            cur.append("~")
    return out, codes, start

HELI = "".join(chr(c) for c in [0x76F4, 0x5347, 0x673A, 0x7A81, 0x51FB])   # 直升机突击
MIWU = "".join(chr(c) for c in [0x8FF7, 0x96FE, 0x5DF7])                    # 迷雾巷

for p in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    try:
        v = Vpp(p)
    except Exception:
        continue
    for e in v.entries():
        if e["ext"] != "le_strings":
            continue
        try:
            b = v.read(e)
            pieces, codes, start = parse(b, M)
        except Exception:
            continue
        for i, (st, en, s) in enumerate(pieces):
            if HELI in s or MIWU in s:
                print("HIT %-14s %-22s piece#%-6d  %r" % (os.path.basename(p), e["name"], i, s))
                print("     codes:", codes[st:en])
                print("     O-decode:", "".join(
                    (chr(O[c-32]) if 32 <= c and c-32 < len(O) else "") for c in codes[st:en]))

print()
print("== the two broken strings: M-decode vs O-decode ==")
v = Vpp(os.path.join(G, "patch.vpp_pc"))
b = v.read(v.find("static_CH", "le_strings"))
pieces, codes, start = parse(b, M)
for pi in (3461, 5231):
    st, en, s = pieces[pi]
    cs = codes[st:en]
    print("piece #%d" % pi)
    print("  M:", "".join((chr(M[c-32]) if 32 <= c and c-32 < len(M) else "") for c in cs))
    print("  O:", "".join((chr(O[c-32]) if 32 <= c and c-32 < len(O) else "") for c in cs))
