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

# 目标槽位序列（用当前 2795 字表）
SEQ = {
  "辩护律师":[2506,1222,1089,1013],
  "辩护延师":[2506,1222,1057,1013],
  "三王":[271,1796],
  "丈王":[270,1796],
}
srcs = [("patch.vpp_pc:static_CH", bytes(v.read(v.find("static_CH","le_strings"))))]
M=os.path.join(G,"Mods")
for f in ("static_CH.le_strings.v44bak","static_CH.le_strings.v45bak",
          "static_CH.le_strings.\u6211\u7684v103.\u5df2\u8ba9\u4f4d.bak"):
    srcs.append((f, open(os.path.join(M,f),"rb").read()))
srcs.append(("DLC/Text/dlc_ch.le_strings", open(os.path.join(G,"DLC","Text","dlc_ch.le_strings"),"rb").read()))

for label, seq in SEQ.items():
    n=len(seq)
    print("=== 目标「%s」槽位 %s ===" % (label, seq))
    for name, d in srcs:
        try: b,c,oa,offs = file_offsets(d)
        except Exception as ex:
            print("   %-38s 解析失败 %s" % (name, ex)); continue
        hits=[]
        for off in dict.fromkeys(offs):
            if not (0 < off <= len(d)-10): continue
            u,_ = read_units(d, off+8)
            if u is None: continue
            vals=[x for x,_ in u]
            for i in range(len(vals)-n+1):
                if vals[i:i+n]==seq:
                    hits.append((off, dec(vals[max(0,i-8):i+12])))
                    break
        print("   %-38s 命中 %d" % (name, len(hits)))
        for off,t in hits[:3]:
            print("        @%-8d ...%s..." % (off, t))
