import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def getuv(p, name, ext):
    v = Vpp(p); e = v.find(name, ext)
    b = v.read(e)
    N = struct.unpack_from('<I', b, 8)[0]
    uo = 0xBC + N*16
    U = [struct.unpack_from('<I', b, uo+i*4)[0] for i in range(N)]
    V = [struct.unpack_from('<I', b, uo+N*4+i*4)[0] for i in range(N)]
    return N, U, V

N2, mU, mV = getuv(os.path.join(G, "common.vpp_pc"), "fnt_chinese", "vf3_pc")
_, oU, oV = getuv(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig", "fnt_chinese", "vf3_pc")

def loadat(p, name, ext):
    v = Vpp(p); e = v.find(name, ext); return v.read(e)

A_cur = dxt3_decode(loadat(os.path.join(G,"patch.vpp_pc"),"fnt_chinese","g_peg_pc"), 2048, 2048)[1]
A_off = dxt3_decode(loadat(r"F:/sr2-cn/vpp_backup/textures.vpp_pc.orig","fnt_chinese",None), 2048, 2048)[1]

vp = Vpp(os.path.join(G,"patch.vpp_pc"))
raw = vp.read(vp.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
nums = [int(s) for s in raw if s.strip().isdigit()]

TEXT = "你的弟兄们"
imgs = []
info = []
for ch in TEXT:
    i = nums.index(ord(ch))
    imgs.append(A_cur[mV[i]:mV[i]+31, mU[i]:mU[i]+31])
    imgs.append(A_off[oV[i]:oV[i]+31, oU[i]:oU[i]+31])
    info.append((ch, i, mU[i], mV[i], oU[i], oV[i]))
strip = np.hstack([np.pad(x, ((3,3),(2,2)), constant_values=0) for x in imgs])
Image.fromarray(strip).save(r"F:/sr2-cn/_DI3_pairs.png")
for r in info:
    print("字=%s charlist_idx=%4d  我的(U=%4d,V=%4d)  官方(U=%4d,V=%4d)" % r)
print("-> _DI3_pairs.png")
