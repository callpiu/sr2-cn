import sys, os
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS=[int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S={i+0x20:chr(cp) for i,cp in enumerate(CPS)}
def dec(vals):
    return "".join(S.get(x, chr(x) if 32<=x<127 else ("\\n" if x==0x0A else "\uFFFD")) for x in vals)
M=r"G:/SteamLibrary/steamapps/common/Saints Row 2/Mods"
import glob
for f in ("static_CH.le_strings.v44bak","static_CH.le_strings.v45bak","static_CH.le_strings.\u6211\u7684v103.\u5df2\u8ba9\u4f4d.bak"):
    p=os.path.join(M,f)
    if not os.path.exists(p): print("缺失",f); continue
    d=open(p,"rb").read()
    print("=== %s  %d 字节 ===" % (f, len(d)))
    try: b,c,oa,offs=file_offsets(d)
    except Exception as ex:
        print("   解析失败",ex); continue
    n=0
    for off in dict.fromkeys(offs):
        if not (0<off<=len(d)-10): continue
        u,_=read_units(d,off+8)
        if u is None: continue
        vals=[x for x,_ in u]; t=dec(vals)
        if "辩" in t or "丈" in t or "三王" in t or "律师" in t or "王" in t and len(t)<=8:
            print("   @%-8d %s" % (off,t[:80].replace("\n"," ")))
            n+=1
            if n>8: break
