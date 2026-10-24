import sys, os, struct
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

def dec(raw, T, order):
    out = []; i = 0
    while i + 1 < len(raw):
        if order == "be": v = (raw[i] << 8) | raw[i+1]
        else: v = raw[i] | (raw[i+1] << 8)
        i += 2
        if v == 0: out.append("\n")
        elif v < 32: out.append("")
        elif v - 32 < len(T): out.append(chr(T[v-32]))
        else: out.append("~")
    return "".join(out)

vp = Vpp(os.path.join(G, "patch.vpp_pc"))
b = vp.read(vp.find("static_CH", "le_strings"))
n = struct.unpack_from("<I", b, 8)[0]
print("static_CH size=%d  n=%d  dirend(16+n*8)=%d" % (len(b), n, 16 + n*8))
print()
PROBE = [0x76F4, 0x5347, 0x673A]   # zhi sheng ji
PROBE_S = "".join(chr(c) for c in PROBE)

best = None
for hdr in (16, 20, 24, 28, 32):
    start = hdr + n * 8
    if start >= len(b): continue
    for order in ("be", "le"):
        for tn, T in (("M", M), ("O", O)):
            s = dec(b[start:], T, order)
            cjk = sum(1 for c in s if 0x4E00 <= ord(c) < 0x9FFF)
            ratio = cjk / max(1, len(s))
            k = s.find(PROBE_S)
            mark = ""
            if k >= 0: mark = "  <<<< HIT PROBE @%d" % k
            print("hdr=%-3d order=%s tbl=%s len=%6d cjk=%6d(%.2f) %s%s" % (hdr, order, tn, len(s), cjk, ratio, repr(s[:60]), mark))
            if k >= 0 and (best is None or ratio > best[0]):
                best = (ratio, hdr, order, tn, k, s)
print()
if best:
    ratio, hdr, order, tn, k, s = best
    print("BEST: hdr=%d order=%s tbl=%s" % (hdr, order, tn))
    print("context:", s[max(0,k-120):k+160].replace("\n", "|"))
