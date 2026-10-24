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

def scan(lesname):
    e=vp.find(lesname,"le_strings")
    if not e: print("MISSING",lesname); return []
    data=vp.read(e)
    magic,ver,buckets,count=struct.unpack_from('<IHHI',data,0)
    off=12+buckets*8
    ptrs=[struct.unpack_from('<I',data,off+i*4)[0] for i in range(count)]
    hits=[]
    for o in ptrs:
        if o+4>len(data): continue
        id1,id2=struct.unpack_from('<HH',data,o)
        p=o+4; chars=[]; cjk_only=[]
        while p+1<len(data):
            s=struct.unpack_from('>H',data,p)[0]
            if s==0: break
            p+=2; ci=s-0x20
            c=chr(cl[ci]) if 0<=ci<len(cl) else '\uFFFD'
            chars.append(c)
            if ci>=95: cjk_only.append((c,ci))
        txt="".join(chars)
        if "弹药" in txt:
            hits.append(((id1<<16)|id2, txt, cjk_only))
    return hits

for f in ["static_CH","platform_pc_CH","voice_script_CH"]:
    hits=scan(f)
    print(f"\n===== {f}: {len(hits)} records containing 弹药 =====")
    for h,txt,_ in hits:
        # show context around 弹药
        i=txt.find("弹药")
        ctx=txt[max(0,i-12):i+14]
        print(f"  hash={h:#010x}  ...{ctx}...")
        print(f"    full: {txt}")
