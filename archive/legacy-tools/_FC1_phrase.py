import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load_charlist(path, name="charlist_CH"):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = load_charlist(os.path.join(G, "patch.vpp_pc"))

def render(b, T):
    n = struct.unpack_from("<I", b, 8)[0]
    start = 16 + n * 8
    if start >= len(b): return []
    nc = (len(b) - start) // 2
    codes = struct.unpack_from(">%dH" % nc, b, start)
    out = []; cur = []; curstart = 0
    for i, c in enumerate(codes):
        if c == 0:
            out.append((curstart, "".join(cur))); cur = []; curstart = i + 1
        elif c < 32: cur.append("")
        elif c - 32 < len(T): cur.append(chr(T[c - 32]))
        else: cur.append("~")
    return out

PHRASES = ["\u4f60\u7684\u5f1f\u5144", "\u9700\u8981\u4f60\u7684\u4fdd\u62a4", "\u5f1f\u5144\u4eec"]
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
for e in vp.entries():
    if "string" not in (e.get("ext") or ""):
        continue
    b = vp.read(e)
    for st, s in render(b, M):
        for p in PHRASES:
            if p in s:
                print("%-26s c%-7d %s" % (e["name"] + "." + e["ext"], st, s[:110]))
print("--- loose ---")
for dp, _, fns in os.walk(os.path.join(G, "Mods")):
    for fn in fns:
        if fn.lower().endswith(".le_strings"):
            fp = os.path.join(dp, fn)
            try:
                b = open(fp, "rb").read()
                for st, s in render(b, M):
                    for p in PHRASES:
                        if p in s:
                            print("%-26s c%-7d %s" % (fn, st, s[:110]))
            except Exception as ex:
                pass
print("done")
