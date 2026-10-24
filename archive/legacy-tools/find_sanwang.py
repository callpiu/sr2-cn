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
# DLC 文件用同款 slot 制
def scan(label, d):
    try: b,c,oa,offs=file_offsets(d)
    except Exception as ex:
        print("%s 解析失败 %s" % (label,ex)); return
    hits=0
    for off in dict.fromkeys(offs):
        if not (0<off<=len(d)-10): continue
        u,_=read_units(d,off+8)
        if u is None: continue
        vals=[x for x,_ in u]; t=dec(vals)
        if "三王" in t or "丈王" in t or "三" in t and "王" in t and len(t)<=6:
            print("  %s @%-8d %s  槽位%s" % (label,off,t, vals[:8])); hits+=1
    if not hits: print("  %s: 无命中" % label)
print("=== DLC/Text/dlc_ch.le_strings ===")
scan("dlc_ch", open(os.path.join(G,"DLC","Text","dlc_ch.le_strings"),"rb").read())
print("=== patch.vpp_pc 内 static_CH 里含「三」的短记录 ===")
d=bytes(v.read(v.find("static_CH","le_strings")))
b,c,oa,offs=file_offsets(d)
n=0
for off in dict.fromkeys(offs):
    if not (0<off<=len(d)-10): continue
    u,_=read_units(d,off+8)
    if u is None: continue
    vals=[x for x,_ in u]; t=dec(vals)
    if "三" in t and len(t)<=8:
        print("  static_CH @%-8d %r 槽位%s" % (off,t,vals)); n+=1
        if n>15: break
