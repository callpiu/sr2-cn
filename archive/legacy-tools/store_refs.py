import sys, struct, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp=S.Vpp(game+"patch.vpp_pc")
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
h2t={}
for o in ptrs:
    if o+4>len(data): continue
    id1,id2=struct.unpack_from('<HH',data,o)
    p=o+4; chars=[]
    while p+1<len(data):
        s=struct.unpack_from('>H',data,p)[0]
        if s==0: break
        p+=2; ci=s-0x20
        chars.append(chr(cl[ci]) if 0<=ci<len(cl) else '\uFFFD')
    h2t[(id1<<16)|id2]="".join(chars)

vc=S.Vpp(game+"common.vpp_pc")
for name in ["store_weapons","ammo","shop_names","store_discounts","weapon_categories"]:
    e=vc.find(name,"xtbl")
    if not e: print("MISSING",name); continue
    buf=vc.read(e)
    refs=set()
    for i in range(0,len(buf)-3):
        h=struct.unpack_from('<I',buf,i)[0]
        if h in h2t: refs.add(h)
    print(f"\n== {name}.xtbl ({len(refs)} str refs) ==")
    for h in sorted(refs):
        print(f"   {h:#010x}  {h2t[h]}")
