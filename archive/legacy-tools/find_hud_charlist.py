#!/usr/bin/env python3
# Find which charlist the activity HUD uses: for the 9 input glyph-indices
# (slot-0x20) the HUD shows 任,璨,偶,巧,位,雄,衡,伪,该. Find the charlist C
# such that C[idx] == garble_char for all 9.
import sr2lib, struct, os

def load_cps_data(d):
    return [int(x) for x in d.decode('utf-8',errors='replace').split() if x.strip().isdigit()]
def load_cps(path):
    with open(path,'rb') as f: d=f.read()
    return load_cps_data(d)

def cp2charlist(cps):
    cp2i={cp:i for i,cp in enumerate(cps)}
    return cp2i

base=r"G:/SteamLibrary/steamapps/common/Saints Row 2"
# candidates: patch charlist_chtxt, jpcharlisttxt, common charlist, pristine 2838
cands={}
vpatch=sr2lib.Vpp(base+r"/patch.vpp_pc")
pe={(e['name']+e.get('ext','')).lower():e for e in vpatch.entries()}
cands['patch_charlist_chtxt']=load_cps_data(vpatch.read(pe['charlist_chtxt']))
cands['patch_jpcharlisttxt']=load_cps_data(vpatch.read(pe['jpcharlisttxt']))

vcommon=sr2lib.Vpp(base+r"/common.vpp_pc")
ce={(e['name']+e.get('ext','')).lower():e for e in vcommon.entries()}
print("common charlist entries:", [k for k in ce if 'charlist' in k or 'charset' in k])
for k in ce:
    if 'charlist' in k or 'charset' in k or 'font' in k:
        try:
            cands['common_'+k]=load_cps_data(vcommon.read(ce[k]))
        except Exception as ex:
            print("  skip",k,ex)

# also pristine 2838 if on disk
for cand_path in [r"F:/sr2-cn/pristine/patch.vpp_pc"]:
    if os.path.isfile(cand_path):
        vp=sr2lib.Vpp(cand_path)
        ppe={(e['name']+e.get('ext','')).lower():e for e in vp.entries()}
        for k in ppe:
            if 'charlist' in k and 'ch' in k:
                cands['pristine_'+k]=load_cps_data(vp.read(ppe[k]))

# input indices and expected garble chars
input_idx=[371,1836,1067,454,364,2699,2328,423,1222]
garble='任璨偶巧位雄衡伪该'  # 9 chars (your 弟兄们需要你的保护)

def cps_to_idxmap(cps):
    return {cp:i for i,cp in enumerate(cps)}

print("\nSearching for charlist_HUD where C[idx]==garble_char for all 9...")
for name,cps in cands.items():
    idxmap=cps_to_idxmap(cps)
    ok=True
    detail=[]
    for idx,gc in zip(input_idx,garble):
        if 0<=idx<len(cps):
            ch=chr(cps[idx])
        else:
            ch='?'
        detail.append(ch)
        if ch!=gc: ok=False
    print(f"  {name:30s} match={ok}  -> {''.join(detail)} (expect {garble})")
