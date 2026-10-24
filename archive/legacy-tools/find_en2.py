import sys, os
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS=[int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S={i+0x20:chr(cp) for i,cp in enumerate(CPS)}
d=bytes(v.read(v.find("static_US","le_strings")))
b,c,oa,offs=file_offsets(d)
CH={i+0x20:cp for i,cp in enumerate(CPS)}
# 找 static_US 中含 king 的短名 + 对应 static_CH
dc=bytes(v.read(v.find("static_CH","le_strings")))
bc,cc,oac,offsc=file_offsets(dc)
def rd(dd,off):
    u,_=read_units(dd,off+8)
    return [x for x,_ in u] if u else None
def dec(vals):
    return "".join(S.get(x, chr(x) if 32<=x<127 else "\uFFFD") for x in vals)
n=0
for off in dict.fromkeys(offs):
    vals=rd(d,off)
    if not vals: continue
    t="".join(chr(x) for x in vals)
    if len(t)<=24 and ("king" in t.lower()) and ("3" in t or "three" in t.lower() or "tri" in t.lower()):
        print("static_US @%-8d %r" % (off,t)); n+=1
        if n>15: break
print("---- static_CH 中长度<=6 且含「王」的记录 ----")
m=0
for off in dict.fromkeys(offsc):
    vals=rd(dc,off)
    if not vals: continue
    t=dec(vals)
    if len(t)<=6 and "王" in t:
        print("  static_CH @%-8d %r 槽位%s" % (off,t,vals)); m+=1
