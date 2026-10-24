import sys, struct, re
sys.path.insert(0,"F:/sr2-cn")
import sr2lib as S
import numpy as np

game="G:/SteamLibrary/steamapps/common/Saints Row 2/"
vp=S.Vpp(game+"patch.vpp_pc")
vc=S.Vpp(game+"common.vpp_pc")

def load_charlist(vp,name):
    e=vp.find(name,"txt"); buf=vp.read(e)
    end=buf.find(b'//ENDOFFILE'); 
    if end<0: end=len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]
cl=load_charlist(vp,"charlist_CH")
cp2ci={cp:i for i,cp in enumerate(cl)}

AT=2048; PITCH=31; COLS=66; X0=2; Y0=34; CELLSZ=31

def decode_atlas(vp,name):
    e=vp.find(name,"peg_pc"); buf=vp.read(e)
    rgb,a=S.dxt3_decode(buf,AT,AT)
    return a.astype(np.float32)/255.0   # coverage mask

patch_a=decode_atlas(vp,"fnt_chineseg_peg_pc")
common_a=decode_atlas(vc,"fnt_chinese")

def cell_mask(atlas,idx):
    if idx<94:  # ASCII row: simple pitch; skip, we only need CJK
        return None
    col=(idx-94)%COLS; row=(idx-94)//COLS
    x=X0+col*PITCH; y=Y0+row*PITCH
    if y+CELLSZ>AT or x+CELLSZ>AT: return None
    m=atlas[y:y+CELLSZ, x:x+CELLSZ]
    # bbox
    ys,xs=np.where(m>0.05)
    if len(xs)==0: return None
    m=m[ys.min():ys.max()+1, xs.min():xs.max()+1]
    if m.shape[0]<2 or m.shape[1]<2: return None
    # resize to 40x40
    from PIL import Image
    im=Image.fromarray((m*255).astype(np.uint8)).resize((40,40))
    r=np.array(im).astype(np.float32)/255.0
    return r

# build patch reference for CJK indices
patch_ref={}
print("building patch reference...")
for idx in range(94, len(cl)):
    m=cell_mask(patch_a,idx)
    if m is not None: patch_ref[idx]=m
print("patch ref cells:", len(patch_ref))

def best_match(target_char_ci):
    tgt=patch_ref.get(target_char_ci)
    if tgt is None: return None
    best=None;bestv=-1
    for idx in range(94, 2838):
        m=cell_mask(common_a,idx)
        if m is None: continue
        # normalized correlation
        a=tgt-tgt.mean(); b=m-m.mean()
        denom=(np.sqrt((a*a).sum())*np.sqrt((b*b).sum()))
        v=(a*b).sum()/denom if denom>1e-6 else -1
        if v>bestv: bestv=v; best=idx
    return best,bestv

# anchors: character -> EXPECTED common cell == its charlist_CH source index? NO.
# We KNOW: HUD index ci renders character G. So common cell [ci] contains G.
# So for G=任, common cell 371 contains 任. => matching patch-任 should return 371.
anchors=['任','璨','偶','巧','位','雄','衡','伪','该']
print("\n-- validate: match patch glyph of anchor char, expect common cell == its original charlist_CH index that garbled TO it --")
# expected: 任<-371, 璨<-1836, 偶<-1035, 巧<-422, 位<-332, 雄<-2667, 衡<-2296, 伪<-391, 该<-1190
exp={'任':371,'璨':1836,'偶':1035,'巧':422,'位':332,'雄':2667,'衡':2296,'伪':391,'该':1190}
for ch in anchors:
    ci=cp2ci[ord(ch)]
    res=best_match(ci)
    if res is None: print(f"  {ch}: no patch ref"); continue
    bi,bv=res
    print(f"  {ch}(patch ci={ci}) -> best common cell={bi} (expected {exp[ch]})  ncc={bv:.3f}")
