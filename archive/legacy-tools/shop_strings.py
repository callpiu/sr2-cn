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

# build hash -> text for static_CH
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
print("static_CH records:",len(h2t))

# find shop-ish xtbls and list referenced strings
pat=re.compile(r'fire|store|shop|weapon|ammo|buy|purchase|merch',re.I)
for e in vp.entries():
    if e['ext'].lower()!='xtbl': continue
    if not pat.search(e['name']): continue
    buf=vp.read(e)
    refs=set()
    for i in range(0,len(buf)-3):
        h=struct.unpack_from('<I',buf,i)[0]
        if h in h2t: refs.add(h)
    # only print if any referenced string contains 弹药 or 武器/购买
    interesting=[h for h in refs if ("弹药" in h2t[h] or "购买" in h2t[h] or "武器" in h2t[h])]
    if interesting:
        print(f"\n== {e['name']}.xtbl ({len(refs)} str refs) ==")
        for h in sorted(interesting):
            print(f"   {h:#010x}  {h2t[h]}")
