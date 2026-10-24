import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def uv(vpp, name, ext):
    v=Vpp(vpp); e=v.find(name,ext)
    if e is None: return None
    b=v.read(e); o=vc0=v.data_start+e['body']
    N=struct.unpack_from('<I',b,8)[0]
    uo=0xBC+N*16
    U=[struct.unpack_from('<I',b,uo+i*4)[0] for i in range(N)]
    V=[struct.unpack_from('<I',b,uo+N*4+i*4)[0] for i in range(N)]
    print("%-42s N=%d  U[:6]=%s V[:6]=%s" % (os.path.basename(vpp)+"/"+name+("."+ext if ext else ""), N, U[:6], V[:6]))
    return N,U,V,b

o = uv(os.path.join(G,"common.vpp_pc"),"fnt_chinese","vf3_pc")
ou= uv(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig","fnt_chinese","vf3_pc")
N2,mU,mV,_ = o
_,oU,oV,_ = ou

def load_at(p,name,ext):
    v=Vpp(p); e=v.find(name,ext); return v.read(e)
at_cur = load_at(os.path.join(G,"patch.vpp_pc"),"fnt_chinese","g_peg_pc")
at_off = load_at(r"F:/sr2-cn/vpp_backup/textures.vpp_pc.orig","fnt_chinese",None)
_,A_cur=dxt3_decode(at_cur,2048,2048); _,A_off=dxt3_decode(at_off,2048,2048)

vp=Vpp(os.path.join(G,"patch.vpp_pc"))
nums=[int(s) for s in vp.read(vp.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n') if s.strip().isdigit()]
TEXT="你的弟兄们"
print("\n『%s』 idx = %s"%(TEXT,[nums.index(ord(c)) for c in TEXT]))
imgs=[]
for ch in TEXT:
    i=nums.index(ord(c))
    imgs.append(A_cur[mV[i]:mV[i]+31, mU[i]:mU[i]+31])   # 我的
    imgs.append(A_off[oV[i]:oV[i]+31, oU[i]:oU[i]+31])   # 官方
strip=np.hstack([np.pad(x,((3,3),(2,2)),constant_values=0) for x in imgs])
Image.fromarray(strip).save(r"F:/sr2-cn/_DI2_pairs.png")
print("→ _DI2_pairs.png (左=我的图集 右=官方图集, 交替)")
