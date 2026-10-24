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
cp2ci={cp:i for i,cp in enumerate(cl)}
# known bad charlist indices (from memory ledger, charlist idx)
bad={1089:'律',271:'三',1098:'必',1090:'徒',1097:'心',1091:'得',2132:'联',380:'会'}
for ch in "填弹药":
    ci=cp2ci.get(ord(ch))
    print(f"{ch}: in charlist_CH={'YES idx='+str(ci) if ci is not None else 'NO!!'}", 
          f"| in bad-ledger={'YES (bad)' if ci in bad else 'no'}")
# frequency of 填 and 料 across static_CH
ent=vp.find("static_CH","le_strings"); data=vp.read(ent)
magic,ver,buckets,count=struct.unpack_from('<IHHI',data,0)
off=12+buckets*8
ptrs=[struct.unpack_from('<I',data,off+i*4)[0] for i in range(count)]
from collections import Counter
cnt=Counter()
for o in ptrs:
    if o+4>len(data): continue
    p=o+4
    while p+1<len(data):
        s=struct.unpack_from('>H',data,p)[0]
        if s==0: break
        p+=2; ci=s-0x20
        if 0<=ci<len(cl): cnt[chr(cl[ci])]+=1
print("\nfrequency in static_CH:")
for ch in "填弹药":
    print(f"  {ch}: {cnt.get(ch,0)} occurrences")
