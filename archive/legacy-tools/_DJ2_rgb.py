import sys, os, struct
import numpy as np
from PIL import Image
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp, dxt3_decode
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
def getuv(p,name,ext):
    v=Vpp(p); b=v.read(v.find(name,ext))
    N=struct.unpack_from('<I',b,8)[0]; uo=0xBC+N*16
    return N,[struct.unpack_from('<I',b,uo+i*4)[0] for i in range(N)],[struct.unpack_from('<I',b,uo+N*4+i*4)[0] for i in range(N)]
def loadat(p,name,ext):
    v=Vpp(p); e=v.find(name,ext); return v.read(e)
N,mU,mV = getuv(os.path.join(G,"common.vpp_pc"),"fnt_chinese","vf3_pc")
_,oU,oV = getuv(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig","fnt_chinese","vf3_pc")
rgb_cur,_ = dxt3_decode(loadat(os.path.join(G,"patch.vpp_pc"),"fnt_chinese","g_peg_pc"),2048,2048)
rgb_off,_ = dxt3_decode(loadat(r"F:/sr2-cn/vpp_backup/patch.vpp_pc.orig","fnt_chinese","g_peg_pc"),2048,2048)
vp=Vpp(os.path.join(G,"patch.vpp_pc"))
raw=vp.read(vp.find("charlist_CH","txt")).decode('utf-8','replace').replace('\r','').split('\n')
nums=[int(s) for s in raw if s.strip().isdigit()]
TEXT="你的弟兄们"
def strip(rgb,U,V,pad=31):
    out=[]
    for ch in TEXT:
        i=nums.index(ord(ch))
        out.append(rgb[V[i]:V[i]+pad, U[i]:U[i]+pad])
    return np.hstack([np.pad(x,((3,3),(2,2),(0,0)),constant_values=0) for x in out])
def grey(rgb):
    return rgb.max(axis=2)
a=grey(strip(rgb_cur,mU,mV)); b=grey(strip(rgb_off,oU,oV))
print("我的图集 RGB strip: min=%d max=%d mean=%.1f 非零=%d"%(a.min(),a.max(),a.mean(),(a>0).sum()))
print("官方图集 RGB strip: min=%d max=%d mean=%.1f 非零=%d"%(b.min(),b.max(),b.mean(),(b>0).sum()))
Image.fromarray(np.hstack([np.pad(a,((6,6),(2,2)),constant_values=0),
                            np.pad(b,((6,6),(2,2)),constant_values=0)])).save(r"F:/sr2-cn/_DJ2_rgb.png")
print("-> _DJ2_rgb.png  左=我的RGB 右=官方RGB")
