#!/usr/bin/env python3
# Reverse-engineer common font index->char via bbox-normalized NCC matching.
import sr2lib, struct, numpy as np

GAME=r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def load_atlas(path, name):
    v=sr2lib.Vpp(path); e={(x['name']+x.get('ext','')).lower():x for x in v.entries()}
    rgb,a=sr2lib.dxt3_decode(v.read(e[name]),2048,2048); return a

patch_a=load_atlas(GAME+r"/patch.vpp_pc",'fnt_chineseg_peg_pc')
common_a=load_atlas(GAME+r"/textures.vpp_pc",'fnt_chinese')

def vf3_uv(path,name,N):
    v=sr2lib.Vpp(path); e={(x['name']+x.get('ext','')).lower():x for x in v.entries()}
    buf=v.read(e[name])
    Voff=len(buf)-N*4
    Uoff=Voff-N*4
    U=np.frombuffer(buf,dtype='<i4',count=N,offset=Uoff)
    V=np.frombuffer(buf,dtype='<i4',count=N,offset=Voff)
    return U,V

PU,PV=vf3_uv(GAME+r"/patch.vpp_pc",'fnt_chinesevf3_pc',2795)
CU,CV=vf3_uv(GAME+r"/common.vpp_pc",'fnt_chinesevf3_pc',2838)

def norm_glyph(atlas,U,V,K,wpad=40):
    x=int(U[K]); y=int(V[K])
    if x<0 or y<0 or x+ wpad>2048 or y+wpad>2048: 
        return None
    cell=atlas[y:y+wpad, x:x+wpad].astype(np.float32)
    # bbox of ink
    ys,xs=np.where(cell>40)
    if len(xs)<5: return None
    cell=cell[ys.min():ys.max()+1, xs.min():xs.max()+1]
    # resize to 32x32
    from PIL import Image
    im=Image.fromarray((cell*255).astype(np.uint8)).resize((32,32))
    a=np.array(im).astype(np.float32)
    a=a-a.mean()
    return a

patch_g={}
for K in range(2795):
    g=norm_glyph(patch_a,PU,PV,K)
    if g is not None: patch_g[K]=g

# charlist_CH
vpatch=sr2lib.Vpp(GAME+r"/patch.vpp_pc")
pe={(e['name']+e.get('ext','')).lower():e for e in vpatch.entries()}
cl=vpatch.read(pe['charlist_chtxt'])
cps=[int(x) for x in cl.decode('utf-8').split() if x.strip().isdigit()]

def match_common(K):
    g=norm_glyph(common_a,CU,CV,K)
    if g is None: return [(0,'?')]
    best=[]
    for k,pg in patch_g.items():
        # shapes must match 32x32
        denom=(np.sqrt((g*g).sum())*np.sqrt((pg*pg).sum()))
        if denom==0: continue
        s=float((g*pg).sum()/denom)
        best.append((s,chr(cps[k]) if 0<=k<len(cps) else '?'))
    best.sort(reverse=True)
    return best[:5]

print("common[371] matches (expect 任):")
for s,c in match_common(371): print(f"   {c!r} {s:.3f}")
print("common[336] (任 patch idx) matches:")
for s,c in match_common(336): print(f"   {c!r} {s:.3f}")
print("common[1836] (的 patch idx) matches:")
for s,c in match_common(1836): print(f"   {c!r} {s:.3f}")
print("common[1067] (弟 patch idx) matches:")
for s,c in match_common(1067): print(f"   {c!r} {s:.3f}")
