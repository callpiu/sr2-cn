import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load_charlist(path, name="charlist_CH"):
    v = Vpp(path); e = v.find(name, "txt")
    if e is None: return None
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = load_charlist(os.path.join(G, "patch.vpp_pc"))
O = load_charlist(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")

def pieces_of(b):
    n = struct.unpack_from("<I", b, 8)[0]
    start = 16 + n * 8
    if start >= len(b): return []
    nc = (len(b) - start) // 2
    codes = struct.unpack_from(">%dH" % nc, b, start)
    out = []; cur = []
    for c in codes:
        if c == 0:
            out.append("".join(cur)); cur = []
        elif c < 32: cur.append("")
        elif c - 32 < len(M): cur.append(chr(M[c - 32]))
        else: cur.append("~")
    return out

def render(b, T):
    n = struct.unpack_from("<I", b, 8)[0]
    start = 16 + n * 8
    nc = (len(b) - start) // 2
    codes = struct.unpack_from(">%dH" % nc, b, start)
    out = []; cur = []
    for c in codes:
        if c == 0:
            out.append("".join(cur)); cur = []
        elif c < 32: cur.append("")
        elif c - 32 < len(T): cur.append(chr(T[c - 32]))
        else: cur.append("~")
    return out

vp = Vpp(os.path.join(G, "patch.vpp_pc"))
vo = Vpp(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")

for nm in ("voice_script_CH", "static_CH"):
    b = vp.read(vp.find(nm, "le_strings"))
    eo = vo.find(nm, "le_strings")
    bo = vo.read(eo) if eo else None
    print("=== %s  current=%d md5=%s | official=%s md5=%s ===" % (
        nm, len(b), hashlib.md5(b).hexdigest()[:10],
        len(bo) if bo else "-", hashlib.md5(bo).hexdigest()[:10] if bo else "-"))
    for tag, T in (("M", M), ("O", O)):
        ps = render(b, T)
        cjk = sum(s.count(c) for s in ps for c in s if 0x4E00 <= ord(c) < 0x9FFF)
        tot = sum(len(s) for s in ps)
        print("   current decoded with %s: pieces=%d chars=%d cjk=%d (%.2f)" % (tag, len(ps), tot, cjk, cjk / max(1, tot)))
    ps = render(b, M)
    print("   sample(M):", " | ".join([x for x in ps if len(x) > 4][:6]))
    print("   sample(O):", " | ".join([x for x in render(b, O) if len(x) > 4][:6]))
    if bo:
        print("   official sample(M):", " | ".join([x for x in render(bo, M) if len(x) > 4][:4]))
        print("   official sample(O):", " | ".join([x for x in render(bo, O) if len(x) > 4][:4]))
    print()
