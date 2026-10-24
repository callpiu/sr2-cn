import sys, os
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S = {i+0x20: chr(cp) for i,cp in enumerate(CPS)}
def dec(vals):
    o=[]
    for x in vals:
        if x in S: o.append(S[x])
        elif 32<=x<127: o.append(chr(x))
        elif x==0x0A: o.append("\\n")
        else: o.append("\uFFFD")
    return "".join(o)
targets = {"辩":2506, "指定":None, "师":1013, "律":1089}
for e in v.entries():
    if e["ext"] not in ("le_strings",""): continue
    d = bytes(v.read(e))
    try: b,c,oa,offs = file_offsets(d)
    except Exception: continue
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        u,_ = read_units(d, off+8)
        if u is None: continue
        vals=[x for x,_ in u]; t=dec(vals)
        if "辩" in t:
            print("%-18s @%-9d %s" % (e["name"], off, t[:120].replace("\n"," ")))
