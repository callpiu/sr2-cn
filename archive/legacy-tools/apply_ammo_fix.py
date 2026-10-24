import sys, struct, re, hashlib, shutil, datetime
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
path=game+"patch.vpp_pc"

vp=S.Vpp(path)
def load_charlist(vp,name):
    e=vp.find(name,"txt"); buf=vp.read(e)
    end=buf.find(b'//ENDOFFILE')
    if end<0: end=len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]
cl=load_charlist(vp,"charlist_CH")
cp2ci={cp:i for i,cp in enumerate(cl)}

ent=vp.find("static_CH","le_strings")
blob_start=vp.data_start+ent['body']
blob=bytes(vp.data[blob_start:blob_start+ent['size']])
magic,ver,buckets,count=struct.unpack_from('<IHHI',blob,0)
off=12+buckets*8
ptrs=[struct.unpack_from('<I',blob,off+i*4)[0] for i in range(count)]

TARGET=0x36B05984
recs=[]
for o in ptrs:
    if o+4>len(blob): continue
    id1,id2=struct.unpack_from('<HH',blob,o)
    if ((id1<<16)|id2)==TARGET: recs.append(o)
print("records with hash 0x36B05984:",len(recs))
assert len(recs)==1, "must be exactly 1 record"
o=recs[0]
p=o+4; slots=[]
while True:
    s=struct.unpack_from('>H',blob,p)[0]
    if s==0: break
    slots.append(s); p+=2
cur="".join(chr(cl[s-0x20]) for s in slots)
print("current decoded text:",repr(cur))
assert cur=="弹药", f"unexpected current text {cur!r}"

new_slots=[cp2ci[ord('填')]+0x20, cp2ci[ord('料')]+0x20]
assert len(new_slots)==len(slots)==2

abs_off=blob_start+o+4
# --- pre-write assertions ---
assert bytes(vp.data[blob_start+o:blob_start+o+4])==struct.pack('<HH',0x36b0,0x5984), "ID mismatch"
cur_bytes=bytes(vp.data[abs_off:abs_off+4])
exp_bytes=b"".join(struct.pack('>H',s) for s in slots)
assert cur_bytes==exp_bytes, f"slot bytes mismatch {cur_bytes.hex()} vs {exp_bytes.hex()}"
assert struct.unpack_from('>H',vp.data,abs_off+4)[0]==0, "missing terminator"
print("pre-write assertions OK; old slot bytes:",exp_bytes.hex(),"-> new:",b"".join(struct.pack('>H',s) for s in new_slots).hex())

# --- backup + in-place write ---
ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
bak=path+f".v{ts}_before_ammo.bak"
shutil.copy2(path,bak)
for i,s in enumerate(new_slots):
    struct.pack_into('>H',vp.data,abs_off+2*i,s)
open(path,'wb').write(bytes(vp.data))
print("backup:",bak)

# --- post-write verify (reload from disk) ---
vp2=S.Vpp(path)
ent2=vp2.find("static_CH","le_strings")
bs2=vp2.data_start+ent2['body']
blob2=bytes(vp2.data[bs2:bs2+ent2['size']])
m2,v2,bk2,c2=struct.unpack_from('<IHHI',blob2,0)
o2=12+bk2*8
ptrs2=[struct.unpack_from('<I',blob2,o2+i*4)[0] for i in range(c2)]
found=None
for oo in ptrs2:
    if oo+4>len(blob2): continue
    i1,i2=struct.unpack_from('<HH',blob2,oo)
    if ((i1<<16)|i2)==TARGET:
        pp=oo+4; sl=[]
        while True:
            s=struct.unpack_from('>H',blob2,pp)[0]
            if s==0: break
            sl.append(s); pp+=2
        found="".join(chr(cl[s-0x20]) for s in sl)
print("post-write decoded:",repr(found))
assert found=="填料", "verify failed"
print("new md5:",hashlib.md5(open(path,'rb').read()).hexdigest())
print("DONE")
