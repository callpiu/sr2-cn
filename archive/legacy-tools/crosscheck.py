import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:/sr2-cn/pylibs"); sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
from sr2patch import file_offsets, read_units
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G,"patch.vpp_pc"))
_, al = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS=[int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S={i+0x20:chr(cp) for i,cp in enumerate(CPS)}
N=struct.unpack_from("<i",vf3,0x08)[0]
U0,V0,NU=0xAF6C,0xDB18,2795
U=list(struct.unpack_from("<%di"%NU,vf3,U0))
V=list(struct.unpack_from("<%di"%NU,vf3,V0))
d=bytes(v.read(v.find("static_CH","le_strings")))
b,c,oa,offs=file_offsets(d)
def dec(vals): return "".join(S.get(x, chr(x) if 32<=x<127 else "\uFFFD") for x in vals)
recs={}
for off in dict.fromkeys(offs):
    if not (0<off<=len(d)-10): continue
    r=read_units(d,off+8)
    if r: recs[off]=[x for x,_ in r[0]]
# 基准1: 葬礼降临斯蒂尔沃特（游戏里正确显示）
b1=recs.get(75856)
# 目标: 辩护律师
b2=recs.get(225978)
print("基准 斯蒂尔沃特 槽位:", b1[4:])
print("目标 辩护律师   槽位:", b2)
print()
groups=[("游戏显示正确的字", b1[4:]), ("出错的字", b2)]
tiles=[]; labels=[]
for gi,(lab,vals) in enumerate(groups):
    for s in vals:
        i=s-0x20
        ch=S.get(s,"?")
        x,y=U[i],V[i]
        g=al[y:y+31, x:x+31]
        tiles.append(255-g); tiles.append(np.full((31,3),160,np.uint8))
        labels.append(ch)
        print("  %-6s slot=%-5d idx=%-5d (%4d,%4d)" % (lab[:4],s,i,x,y))
s=np.concatenate(tiles,axis=1)
Image.fromarray(s).resize((s.shape[1]*11,s.shape[0]*11),Image.NEAREST).save(r"F:/sr2-cn/_juice_fix/crosscheck.png")
print("\n顺序:", " ".join(labels))
