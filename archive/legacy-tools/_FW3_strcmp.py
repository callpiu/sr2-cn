"""FW3: compare the reference patch's static_CH / voice_script_CH with ours,
and check what codes the reference uses for the two target sentences.
"""
import sys, os, struct, hashlib, re
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
REF = r"F:\sr2-cn\_ref92\黑道圣徒2简体汉化补丁\patch.vpp_pc"

def cl(path, name):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = cl(os.path.join(G, "patch.vpp_pc"), "charlist_CH")

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

vr = Vpp(REF)
vm = Vpp(os.path.join(G, "patch.vpp_pc"))

for nm in ("static_CH", "voice_script_CH", "platform_pc_CH"):
    er = vr.find(nm, "le_strings")
    em = vm.find(nm, "le_strings")
    if er is None or em is None:
        print("%-18s ref=%s mine=%s" % (nm, er is not None, em is not None)); continue
    br = vr.read(er); bm = vm.read(em)
    nr = struct.unpack_from("<I", br, 8)[0]; nmv = struct.unpack_from("<I", bm, 8)[0]
    print("%-18s ref size=%-9d n=%-7d md5=%s" % (nm, len(br), nr, hashlib.md5(br).hexdigest()[:12]))
    print("%-18s min size=%-9d n=%-7d md5=%s" % ("", len(bm), nmv, hashlib.md5(bm).hexdigest()[:12]))
    print("     identical:", br == bm)

KEY = "".join(chr(c) for c in [0x9700, 0x8981, 0x4F60, 0x7684, 0x4FDD, 0x62A4])
KEY2 = "".join(chr(c) for c in [0x8C08, 0x51E0, 0x7B14, 0x751F, 0x610F])

for tag, v, name in (("REF", vr, "static_CH"), ("MINE", vm, "static_CH")):
    b = v.read(v.find(name, "le_strings"))
    pieces, codes, start = parse(b, M)
    print()
    print("== %s %s : pieces=%d ==" % (tag, name, len(pieces)))
    for i, (st, en, s) in enumerate(pieces):
        if KEY in s or KEY2 in s:
            print("   piece#%-6d codes[%d..%d)" % (i, st, en))
            print("      %r" % s)
            print("      codes:", codes[st:en])
