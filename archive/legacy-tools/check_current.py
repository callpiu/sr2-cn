import sys, struct, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp=S.Vpp(game+"patch.vpp_pc")   # CURRENT deployed (build_fix v533)
def load_charlist(vp,name):
    e=vp.find(name,"txt"); buf=vp.read(e)
    end=buf.find(b'//ENDOFFILE'); 
    if end<0: end=len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]
cl=load_charlist(vp,"charlist_CH")
ent=vp.find("static_CH","le_strings"); data=vp.read(ent)
magic,ver,buckets,count=struct.unpack_from('<IHHI',data,0)
off=12+buckets*8
ptrs=[struct.unpack_from('<I',data,off+i*4)[0] for i in range(count)]
def decode(off):
    id1,id2=struct.unpack_from('<HH',data,off); p=off+4; chars=[]
    while True:
        s=struct.unpack_from('>H',data,p)[0]
        if s==0: break
        p+=2; ci=s-0x20
        chars.append(chr(cl[ci]) if 0<=ci<len(cl) else '?')
    return (id1<<16)|id2, "".join(chars)
for t in [0x84F287ED,0x10AF1E62]:
    for o in ptrs:
        h,txt=decode(o)
        if h==t:
            print(f"CURRENT {t:#010x}: {txt}")
            break
import hashlib
print("current patch md5:", hashlib.md5(open(game+"patch.vpp_pc",'rb').read()).hexdigest())
print("backup v532 md5:", hashlib.md5(open(game+"patch.vpp_pc.v532_before_exp.bak",'rb').read()).hexdigest())
