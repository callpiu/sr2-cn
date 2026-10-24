import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

# 官方 vf3 的 U/V
vf = Vpp(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig").read(
     Vpp(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig").find("fnt_chinese","vf3_pc"))
N=2838; H=0xBC; uo=H+N*16
oU=[struct.unpack_from('<I',vf,uo+i*4)[0] for i in range(N)]
oV=[struct.unpack_from('<I',vf,uo+N*4+i*4)[0] for i in range(N)]

# 我的 vf3
vc = Vpp(os.path.join(G,"common.vpp_pc"))
ec = vc.find("fnt_chinese","vf3_pc"); o=vc.data_start+ec['body']
N2=struct.unpack_from('<I',vc.data,o+8)[0]
mU=[struct.unpack_from('<I',vc.data,o+uo+i*4)[0] for i in range(N2)]
mV=[struct.unpack_from('<I',vc.data,o+uo+N2*4+i*4)[0] for i in range(N2)]
print("我的 vf3 N=%d  前12 U=%s"%(N2,mU[:12]))
print("            前12 V=%s"%mV[:12])

def load_at(p,name,ext):
    v=Vpp(p); e=v.find(name,ext); return v.read(e)

at_cur  = load_at(os.path.join(G,"patch.vpp_pc"),"fnt_chinese","g_peg_pc")
at_off  = load_at(r"F:/sr2-cn/vpp_backup/textures.vpp_pc.orig","fnt_chinese",None)
_,A_cur = dxt3_decode(at_cur,2048,2048)
_,A_off = dxt3_decode(at_off,2048,2048)

TEXT="你的弟兄们"
nums=[int(s) for s in Vpp(os.path.join(G,"patch.vpp_pc")).read(
      Vpp(os.path.join(G,"patch.vpp_pc")).find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
      if s.strip().isdigit()]
print("\n『%s』的 charlist idx = %s"%(TEXT,[nums.index(ord(c)) for c in TEXT]))
rows=[]
for ch in TEXT:
    i=nums.index(ord(ch))
    u,v=mU[i],mV[i]; ou,ov=oU[i],oV[i]
    rows.append(("我的 idx=%d @(%d,%d)"%(i,u,v), A_cur[v:v+31,u:u+31]))
    rows.append(("官方 idx=%d @(%d,%d)"%(i,ou,ov), A_off[ov:ov+31,ou:ou+31]))
imgs=[x[1] for x in rows]
strip=np.hstack([np.pad(x,((3,3),(2,2)),constant_values=0) for x in imgs])
Image.fromarray(strip).save(r"F:/sr2-cn/_DI_pairs.png")
print("→ _DI_pairs.png  左列=我的图集, 右列=官方图集")
