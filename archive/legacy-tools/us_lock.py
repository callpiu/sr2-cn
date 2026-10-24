# -*- coding: utf-8 -*-
import sys, struct, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp=S.Vpp(game+"patch.vpp_pc")
def dec(les,cl=None):
    e=vp.find(les,"le_strings"); data=vp.read(e)
    m,v,bk,c=struct.unpack_from('<IHHI',data,0); off=12+bk*8
    ptrs=[struct.unpack_from('<I',data,off+i*4)[0] for i in range(c)]
    out={}
    for o in ptrs:
        if o+4>len(data): continue
        i1,i2=struct.unpack_from('<HH',data,o); p=o+4; ch=[]
        while p+1<len(data):
            s=struct.unpack_from('>H',data,p)[0]
            if s==0: break
            p+=2
            if cl is None: ch.append(chr(s) if 32<=s<127 else '')
            else:
                ci=s-0x20; ch.append(chr(cl[ci]) if 0<=ci<len(cl) else '\uFFFD')
        out[(i1<<16)|i2]="".join(ch)
    return out
buf=vp.read(vp.find("charlist_CH","txt")); end=buf.find(b'//ENDOFFILE')
cl=[int(x) for x in re.findall(rb'\d+', buf[:end if end>0 else len(buf)])]
US=dec("static_US"); CH=dec("static_CH",cl)

print("=== 两个已知 hash 的【英文原文】===")
for h in (0x84F287ED,0x10AF1E62):
    print(f"{h:#010x}\n   EN: {US.get(h,'<US表里没有!>')}\n   CN: {CH.get(h,'<无>').rstrip()}")

print("\n=== 英文表里含 'homies need' / 'protect them' / 'heading out' 的记录 ===")
for h,t in US.items():
    tl=t.lower()
    if "homies need" in tl or "protect them" in tl or "heading out" in tl or "deals" in tl:
        cn=CH.get(h); 
        n=sum(1 for c in (cn or '') if ord(c)>0x2000)
        print(f"  {h:#010x} CJK={n}\n     EN: {t[:100]}\n     CN: {(cn or '<无>').rstrip()[:100]}")

print("\n=== 中文表里 CJK 数恰好=22 且含「保护」的记录 ===")
cnt=0
for h,cn in CH.items():
    n=sum(1 for c in cn if ord(c)>0x2000)
    if n==22 and "保护" in cn:
        cnt+=1
        print(f"  {h:#010x}  {cn.rstrip()[:80]}")
        print(f"       EN: {US.get(h,'<无>')[:90]}")
print("  合计:",cnt)
