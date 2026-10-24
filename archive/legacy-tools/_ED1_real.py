import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def get(p):
    v=Vpp(p); return v.read(v.find("static_CH","le_strings"))
def cl(p):
    v = Vpp(p); t = v.read(v.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
    return [int(s) for s in t if s.strip().isdigit()]
A = get(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig"); O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")
B = get(os.path.join(G,"patch.vpp_pc")); M = cl(os.path.join(G,"patch.vpp_pc"))
def dec(x, T):
    n = struct.unpack_from('<I', x, 8)[0]
    start = 16 + n*8 + 1
    codes = struct.unpack_from("<%dH"%((len(x)-start)//2), x, start)
    out = []
    for c in codes:
        if c == 0: out.append("\n")
        elif c-32 < len(T) and c >= 32: out.append(chr(T[c-32]))
        else: out.append("{%d}"%c)
    return "".join(out)
ta = dec(A, O)
tb = dec(B, M)
for tag, t in (("官方解码", ta), ("当前解码", tb)):
    print("=== %s ===" % tag)
    for ln in t.split("\n"):
        if ln.strip(): print("   ", ln[:76])
    print()
