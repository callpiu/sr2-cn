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
def dec(x, T, limit=60):
    n = struct.unpack_from('<I', x, 8)[0]
    start = 16 + n*8
    raw = x[start:]
    out=[]; strings=[]; cur=[]
    i=0
    while i+1 < len(raw) and len(strings) < limit:
        v = (raw[i]<<8) | raw[i+1]; i+=2
        if v == 0:
            strings.append("".join(cur)); cur=[]
        elif v < 32:
            cur.append("<%d>"%v)
        elif v < 0x8000:
            k = v-32
            cur.append(chr(T[k]) if 0 <= k < len(T) else "{%X}"%v)
        else:
            cur.append("{%X}"%v)
    if cur: strings.append("".join(cur))
    return strings
sa = dec(A, O); sb = dec(B, M)
print("=== official (first 25 strings) ===")
for s in sa[:25]: print("   ", s[:70])
print()
print("=== current (first 25 strings) ===")
for s in sb[:25]: print("   ", s[:70])
