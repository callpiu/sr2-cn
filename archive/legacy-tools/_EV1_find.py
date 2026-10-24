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

T3 = "".join(chr(c) for c in [0x4EFB, 0x74A8, 0x5076])            # ren can ou
T5 = "".join(chr(c) for c in [0x4EFB, 0x74A8, 0x5076, 0x5DE7, 0x4F4D])

def dec_be(raw, T):
    out = []; i = 0
    while i + 1 < len(raw):
        v = (raw[i] << 8) | raw[i+1]; i += 2
        if v == 0: out.append("\n")
        elif v < 32: out.append("")
        elif v - 32 < len(T): out.append(chr(T[v-32]))
        else: out.append("?")
    return "".join(out)

def dec_le(raw, T):
    out = []; i = 0
    while i + 1 < len(raw):
        v = raw[i] | (raw[i+1] << 8); i += 2
        if v == 0: out.append("\n")
        elif v < 32: out.append("")
        elif v - 32 < len(T): out.append(chr(T[v-32]))
        else: out.append("?")
    return "".join(out)

for f in ("patch.vpp_pc", "common.vpp_pc"):
    p = os.path.join(G, f)
    v = Vpp(p)
    print("=== %s ===" % f)
    for e in v.entries():
        ext = e.get("ext") or ""
        if "string" not in ext:
            continue
        b = v.read(e)
        print("  --- %s.%s  %d bytes  head=%s" % (e["name"], ext, len(b), b[:24].hex()))
        cand = []
        for ename, fmt in (("le", "<I"), ("be", ">I")):
            try:
                n = struct.unpack_from(fmt, b, 8)[0]
            except Exception:
                continue
            if 0 < n < 200000:
                cand.append((ename, n))
        for ename, n in cand:
            start = 16 + n * 8
            if start >= len(b):
                continue
            raw = b[start:]
            for tn, T in (("M", M), ("O", O)):
                for dn, fn in (("be", dec_be), ("le", dec_le)):
                    s = fn(raw, T)
                    k5 = s.find(T5); k3 = s.find(T3)
                    if k5 >= 0 or k3 >= 0:
                        k = k5 if k5 >= 0 else k3
                        print("     [HIT] n=%d(%s) table=%s order=%s  at=%d" % (n, ename, tn, dn, k))
                        print("        ctx: %s" % s[max(0,k-50):k+70].replace("\n", "|"))
    print()
print("done")
