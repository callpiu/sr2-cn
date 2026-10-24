import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(G + r"\patch.vpp_pc")
_, al3 = dxt3_decode(bytes(v.read(v.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf3 = bytes(v.read(v.find("fnt_chinese","vf3_pc")))
CPS3 = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N = struct.unpack_from("<i", vf3, 0x08)[0]
U0 = 0xD0 + N*16
U = list(struct.unpack_from("<%di"%N, vf3, U0))
nV=(len(vf3)-(U0+N*4))//4
V = list(struct.unpack_from("<%di"%nV, vf3, U0+N*4))

# 原厂做对照：原厂的字表与图集一定是配套的
W = r"F:\sr2-cn"
v0 = Vpp(os.path.join(W,"pristine","patch.vpp_pc"))
_, al0 = dxt3_decode(bytes(v0.read(v0.find("fnt_chinese","g_peg_pc"))), 2048, 2048)
vf30 = bytes(v0.read(v0.find("fnt_chinese","vf3_pc")))
CPS0 = [int(l) for l in v0.read(v0.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
N0 = struct.unpack_from("<i", vf30, 0x08)[0]
U00 = 0xD0 + N0*16
U0a = list(struct.unpack_from("<%di"%N0, vf30, U00))
nV0=(len(vf30)-(U00+N0*4))//4
V0a = list(struct.unpack_from("<%di"%nV0, vf30, U00+N0*4))

def tile(al, U, V, idx, box=31, h=28):
    x,y = U[idx], V[idx]
    return al[y:y+h, x:x+box]

# 检查原厂：字表索引与图集是否一致（用「律」「延」比对）
def show(which, al, U, V, CPS, path):
    tiles=[]; labs=[]
    for ch in which:
        cp = ord(ch)
        if cp not in CPS:
            tiles.append(np.zeros((28,31),np.uint8)); labs.append(ch+"?"); continue
        i = CPS.index(cp)
        tiles.append(tile(al,U,V,i)); labs.append("%s i%d"%(ch,i))
        tiles.append(np.zeros((28,2),np.uint8))
    s=np.concatenate(tiles,axis=1)
    Image.fromarray(255-s).resize((s.shape[1]*8,s.shape[0]*8),Image.NEAREST).save(path)
    return labs
print("原厂（字表与图集配套）:")
labs = show("辩护律师延丈文王", al0, U0a, V0a, CPS0, os.path.join(W,"_juice_fix","orig_glyphs.png"))
print("  %s" % " | ".join(labs))
print()
print("第三方:")
labs2 = show("辩护律师延丈文王", al3, U, V, CPS3, os.path.join(W,"_juice_fix","third_glyphs.png"))
print("  %s" % " | ".join(labs2))
