"""FL2: scan EVERY .le_strings in the game install, decode with M, and report
every piece whose text contains the two target sentences.  This tells us which
file the subtitle really comes from.
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

def parse(b, T):
    if len(b) < 16:
        return [], [], 0
    n = struct.unpack_from("<I", b, 8)[0]
    start = 16 + n * 8
    if start > len(b):
        return [], [], 0
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

KEY = "".join(chr(c) for c in [0x9700, 0x8981, 0x4F60, 0x7684, 0x4FDD, 0x62A4])   # 需要你的保护
KEY2 = "".join(chr(c) for c in [0x8C08, 0x51E0, 0x7B14, 0x751F, 0x610F])           # 谈几笔生意

files = []
for p in sorted(glob.glob(os.path.join(G, "*.vpp_pc"))):
    try:
        v = Vpp(p)
    except Exception:
        continue
    for e in v.entries():
        if e["ext"] == "le_strings":
            files.append((os.path.basename(p), e))
print("le_strings entries:", len(files))

for src, e in files:
    if not (e["name"].endswith("_CH") or e["name"].endswith("_US") or "_CH" in e["name"]):
        continue
    try:
        v = Vpp(os.path.join(G, src)); b = v.read(e)
        pieces, codes, start = parse(b, M)
    except Exception as ex:
        print("  !!", src, e["name"], ex); continue
    for i, (st, en, s) in enumerate(pieces):
        if KEY in s or KEY2 in s:
            abs_st = start + st * 2
            print("HIT  %-16s %-24s piece#%-6d codes[%d..%d)  fileoff=0x%X" % (
                src, e["name"], i, st, en, abs_st))
            print("       %r" % s)
            print("       codes:", codes[st:en])
