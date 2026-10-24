import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
def cl(p):
    v = Vpp(p); t = v.read(v.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
    return [int(s) for s in t if s.strip().isdigit()]
M = cl(os.path.join(G,"patch.vpp_pc"))
O = cl(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")
b = Vpp(os.path.join(G,"patch.vpp_pc")).read(Vpp(os.path.join(G,"patch.vpp_pc")).find("static_CH","le_strings"))
n = struct.unpack_from('<I', b, 8)[0]
lang = struct.unpack_from('<I', b, 12)[0]
dirstart = 16; dirend = dirstart + n*8
ents = [struct.unpack_from('<II', b, dirstart+i*8) for i in range(n)]
p = dirend; ok=True
for i,(sid,ln) in enumerate(ents):
    if p + ln*2 > len(b): ok=False; break
    p += ln*2
print("n=%d lang=%d dirend=%d  walk终点=%d 文件=%d  精确=%s" % (n, lang, dirend, p, len(b), p==len(b)))
def dec(codes, T):
    out=[]
    for c in codes:
        if c==0: out.append("|")
        elif c<32: out.append("<%d>"%c)
        elif c-32 < len(T): out.append(chr(T[c-32]))
        else: out.append("{%d}"%c)
    return "".join(out)
hits=0
for i,(sid,ln) in enumerate(ents):
    codes = struct.unpack_from("<%dH"%ln, b, dirend + (sum(e[1] for e in ents[:i]))*2)
    s = dec(codes, M)
    if any(0x4E00<=ord(c)<0x9FFF for c in s):
        hits+=1
        if hits<=12: print("  [%d] id=0x%08X len=%d  %s" % (i, sid, ln, s[:70]))
print("含汉字的条目数:", hits, "/", n)
