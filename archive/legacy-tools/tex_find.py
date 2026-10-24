import sys, struct
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
TEX="G:/SteamLibrary/steamapps/common/Saints Row 2/textures.vpp_pc"
def hdr(path):
    with open(path,'rb') as f: d=f.read(5+0x14F+20)
    o=5+0x14F
    num,cs,lo,lf,le=struct.unpack_from('<iiiii',d,o)
    names_at=((0x800+lo)&0xFFFFF800)+0x800
    ext_at=((names_at+lf)&0xFFFFF800)+0x800
    data_start=((ext_at+le)&0xFFFFF800)+0x800
    return num,data_start,names_at,ext_at,lo,lf,le
num,ds,names_at,ext_at,lo,lf,le=hdr(TEX)
with open(TEX,'rb') as f:
    f.seek(0x800); etab=f.read(num*28)
    f.seek(names_at); names=f.read(lf+400)
    f.seek(ext_at); exts=f.read(le+400)
def gs(b,o):
    e=b.find(b'\x00',o); return b[o:e].decode('ascii','replace')
for i in range(num):
    a,b,c,d,ln,m1,z=struct.unpack_from('<IIiiiii',etab,i*28)
    n=gs(names,a); x=gs(exts,b) if b else ''
    if n=='fnt_chinese':
        print("FOUND: name=",repr(n),"ext=",repr(x),"body=",ds+d,"size=",ln)
