import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load_charlist(path, name="charlist_CH"):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = load_charlist(os.path.join(G, "patch.vpp_pc"))
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
b = vp.read(vp.find("static_CH", "le_strings"))
n = struct.unpack_from("<I", b, 8)[0]
start = 16 + n * 8
ncodes = (len(b) - start) // 2
codes = struct.unpack_from(">%dH" % ncodes, b, start)
print("codes =", ncodes, " pieces will follow")

pieces = []
cur = []; curstart = 0
for i, c in enumerate(codes):
    if c == 0:
        pieces.append((curstart, i, "".join(cur)))
        cur = []; curstart = i + 1
    elif c < 32:
        cur.append("")
    elif c - 32 < len(M):
        cur.append(chr(M[c - 32]))
    else:
        cur.append("~")
print("pieces =", len(pieces))
print()

KW = ["直升机", "面包车", "停靠", "突击", "掩护", "搭档"]
seen = set()
for idx, (st, en, s) in enumerate(pieces):
    if any(k in s for k in KW):
        for j in range(max(0, idx - 5), min(len(pieces), idx + 6)):
            if j in seen: continue
            seen.add(j)
            pj = pieces[j]
            mark = "   <<<" if j == idx else ""
            print("[%5d] c%-6d %s%s" % (j, pj[0], pj[2][:72], mark))
        print()
