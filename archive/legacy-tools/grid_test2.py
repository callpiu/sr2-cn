import sys, struct
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
import numpy as np
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp=S.Vpp(game+"patch.vpp_pc"); TEX=game+"textures.vpp_pc"
def hdr(path):
    with open(path,'rb') as f: d=f.read(5+0x14F+20)
    o=5+0x14F; num,cs,lo,lf,le=struct.unpack_from('<iiiii',d,o)
    names_at=((0x800+lo)&0xFFFFF800)+0x800; ext_at=((names_at+lf)&0xFFFFF800)+0x800
    data_start=((ext_at+le)&0xFFFFF800)+0x800
    return num,data_start,names_at,ext_at,lo,lf,le
num,ds,na,ea,lo,lf,le=hdr(TEX)
with open(TEX,'rb') as f:
    f.seek(0x800); etab=f.read(num*28); f.seek(na); names=f.read(lf+400); f.seek(ea); exts=f.read(le+400)
def gs(b,o):
    e=b.find(b'\x00',o); return b[o:e].decode('ascii','replace')
cb=None
for i in range(num):
    a,b2,c,d,ln,m1,z=struct.unpack_from('<IIiiiii',etab,i*28)
    if gs(names,a)=='fnt_chinese':
        with open(TEX,'rb') as f: f.seek(ds+d); cb=f.read(ln)
pa=np.array(S.dxt3_decode(vp.read(vp.find("fnt_chinese","g_peg_pc")),2048,2048)[1]).astype(np.float32)
ca=np.array(S.dxt3_decode(cb,2048,2048)[1]).astype(np.float32)
for nm,a in [("PATCH",pa),("COMMON",ca)]:
    col_prof=(a[34:1333,:]>0.1).sum(0).astype(float)
    row_prof=(a[:,2:2046]>0.1).sum(1).astype(float)
    def peaks(prof,lo,hi):
        prof=prof-prof.mean()
        ac=np.correlate(prof,prof,'full')[len(prof)-1:]
        vals=sorted(((ac[l],l) for l in range(lo,hi)),reverse=True)[:5]
        return vals
    print(f"{nm} col top lags:", [(l,round(v)) for v,l in peaks(col_prof,20,45)])
    print(f"{nm} row top lags:", [(l,round(v)) for v,l in peaks(row_prof,20,45)])
    # gap positions: columns with near-zero ink
    lowcols=np.where(col_prof<col_prof.mean()*0.15)[0]
    print(f"{nm} low-ink cols (first 40):", lowcols[:40].tolist())
