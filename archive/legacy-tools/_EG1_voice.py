import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def cl(p):
    v = Vpp(p); t = v.read(v.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
    return [int(s) for s in t if s.strip().isdigit()]
O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")
M = cl(os.path.join(G,"patch.vpp_pc"))
b = Vpp(os.path.join(G,"patch.vpp_pc")).read(Vpp(os.path.join(G,"patch.vpp_pc")).find("voice_script_CH","le_strings"))
n = struct.unpack_from('<I', b, 8)[0]
raw = b[16+n*8:]
def dec(raw, T):
    out=[]; cur=[]
    i=0
    while i+1 < len(raw):
        v=(raw[i]<<8)|raw[i+1]; i+=2
        if v==0:
            out.append("".join(cur)); cur=[]
        elif v<32: cur.append("<%d>"%v)
        elif v<0x8000:
            k=v-32
            cur.append(chr(T[k]) if 0<=k<len(T) else "{%X}"%v)
        else: cur.append("{%X}"%v)
    if cur: out.append("".join(cur))
    return out
sM = dec(raw, M); sO = dec(raw, O)
print("总行数:", len(sM))
import re
for tag, s in (("用我的表", sM), ("用官方表", sO)):
    hits = [x for x in s if ('\u5144' in x or '\u5F1F' in x) and len(x) > 6]
    print("\n=== %s 命中 '兄/弟' 的行 (%d) ===" % (tag, len(hits)))
    for h in hits[:8]: print("   ", h[:80])
