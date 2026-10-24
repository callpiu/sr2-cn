import sys, os
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS=[int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S={i+0x20:chr(cp) for i,cp in enumerate(CPS)}
du=bytes(v.read(v.find("static_US","le_strings")))
dc=bytes(v.read(v.find("static_CH","le_strings")))
def load(d):
    b,c,oa,offs=file_offsets(d)
    out={}
    for off in dict.fromkeys(offs):
        if not (0<off<=len(d)-10): continue
        r=read_units(d,off+8)
        if not r: continue
        out[off]=[x for x,_ in r[0]]
    return out
U=load(du); C=load(dc)
def dec(vals): return "".join(S.get(x, chr(x) if 32<=x<127 else "\uFFFD") for x in vals)
print("=== static_US 含 'King' 短条目 → 中文 ===")
n=0
for o in sorted(U):
    tu="".join(chr(x) for x in U[o])
    if 0<len(tu)<=14 and "king" in tu.lower():
        tc = dec(C[o]) if o in C else "(无CH条目)"
        print("  @%-8d US=%-16r CH=%r" % (o,tu,tc)); n+=1
        if n>=25: break
