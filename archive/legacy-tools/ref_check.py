import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
from sr2patch import file_offsets, read_units
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS=[int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S={i+0x20:chr(cp) for i,cp in enumerate(CPS)}
d=bytes(v.read(v.find("static_CH","le_strings")))
b,c,oa,offs=file_offsets(d)
def dec(vals): return "".join(S.get(x, chr(x) if 32<=x<127 else "\uFFFD") for x in vals)
# 找游戏里显示正常的词作基准
targets=["老斯蒂尔沃特","前往郊区","指定辩护律师","任务"]
found={}
for off in dict.fromkeys(offs):
    if not (0<off<=len(d)-10): continue
    r=read_units(d,off+8)
    if not r: continue
    vals=[x for x,_ in r[0]]; t=dec(vals)
    for w in targets:
        if w in t and w not in found:
            found[w]=(off,vals,t)
for w in targets:
    if w in found:
        off,vals,t=found[w]
        print("%-10s @%-8d  %r" % (w,off,t[:50]))
        print("           slot 序列: %s" % vals[:20])
    else:
        print("%-10s 未找到" % w)
