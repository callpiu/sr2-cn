#!/usr/bin/env python3
# Reverse-engineer the common Chinese font's index->char map by pixel-matching
# each common glyph against the patch font's known glyphs. Then determine which
# font the activity HUD uses (does common[371] render as 任 or 你?).
import sr2lib, struct, numpy as np

GAME=r"G:/SteamLibrary/steamapps/common/Saints Row 2"
def dxt3_block_decode_blockwise(data, w, h):
    return sr2lib.dxt3_decode(data, w, h)

# ---- patch font (reference, known chars) ----
vpatch=sr2lib.Vpp(GAME+r"/patch.vpp_pc")
pe={(e['name']+e.get('ext','')).lower():e for e in vpatch.entries()}
patch_vf3=vpatch.read(pe['fnt_chinesevf3_pc'])
patch_rgb,patch_alpha=dxt3_block_decode_blockwise(vpatch.read(pe['fnt_chineseg_peg_pc']),2048,2048)
patch_atlas=patch_alpha
PU=np.frombuffer(patch_vf3, np.int32); # whole as int32 view, but need offsets
Np=2795
PUa=np.frombuffer(patch_vf3, dtype='<i4', count=Np, offset=0xAF6C)
PVa=np.frombuffer(patch_vf3, dtype='<i4', count=Np, offset=0xDB18)

# charlist_CH to know patch glyph K's character
cl=vpatch.read(pe['charlist_chtxt'])
cps=[int(x) for x in cl.decode('utf-8').split() if x.strip().isdigit()]
cp2i={cp:i for i,cp in enumerate(cps)}

def glyph_img(atlas, U, V, size=32):
    # U,V are top-left of cell; extract size x size alpha
    y0=max(0,int(V)); x0=max(0,int(U))
    a=atlas[y0:y0+size, x0:x0+size]
    return a.astype(np.float32)

def ncc(a,b):
    a=a-a.mean(); b=b-b.mean()
    denom=(np.sqrt((a*a).sum())*np.sqrt((b*b).sum()))
    if denom==0: return 0
    return float((a*b).sum()/denom)

# Build patch glyph cache (only ASCII + sample) -> we'll match against all 2795
print("building patch glyph images...")
patch_chars={}
patch_imgs=[]
for K in range(Np):
    patch_chars[K]=chr(cps[K]) if 0<=K<len(cps) else '?'
    patch_imgs.append(glyph_img(patch_atlas, PUa[K], PVa[K]))

# ---- common font ----
vcommon=sr2lib.Vpp(GAME+r"/common.vpp_pc")
ce={(e['name']+e.get('ext','')).lower():e for e in vcommon.entries()}
common_vf3=vcommon.read(ce['fnt_chinesevf3_pc'])
Nc=2838
# compute U/V offsets from records end
rec_end=0xD0+Nc*16
Uoff=0xB21C
Voff=0xDE4C
print(f"common rec_end={rec_end:#x} Uoff={Uoff:#x} Voff={Voff:#x}")
CUa=np.frombuffer(common_vf3, dtype='<i4', count=Nc, offset=Uoff)
CVa=np.frombuffer(common_vf3, dtype='<i4', count=Nc, offset=Voff)
print("common U[371],V[371]=",CUa[371],CVa[371]," U[0..3]=",CUa[:4]," V[0..3]=",CVa[:4])

# common atlas: textures.vpp_pc fnt_chinese
vt=sr2lib.Vpp(GAME+r"/textures.vpp_pc")
te={(e['name']+e.get('ext','')).lower():e for e in vt.entries()}
print("textures fnt_chinese entry:", 'fnt_chinese' in te, te.get('fnt_chinese'))
common_rgb,common_alpha=dxt3_block_decode_blockwise(vt.read(te['fnt_chinese']),2048,2048)
common_atlas=common_alpha

def match_common_glyph(K, topn=5):
    img=glyph_img(common_atlas, CUa[K], CVa[K])
    scores=[(ncc(img, p), i) for i,p in enumerate(patch_imgs)]
    scores.sort(reverse=True)
    return [(s, patch_chars[i]) for s,i in scores[:topn]]

print("\ncommon glyph 371 best matches (expect 任 or 你):")
for s,c in match_common_glyph(371): print(f"   {c!r}  ncc={s:.3f}")
print("common glyph 336 best matches (任's patch idx):")
for s,c in match_common_glyph(336): print(f"   {c!r}  ncc={s:.3f}")
print("common glyph 1836 best matches (的's patch idx):")
for s,c in match_common_glyph(1836): print(f"   {c!r}  ncc={s:.3f}")
