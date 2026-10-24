#!/usr/bin/env python3
# Scan every charlist-like entry across all VPP files in the game dir and test
# whether C[idx]==garble_char for the 9 activity input indices. The matching
# charlist is the activity HUD's font ordering.
import sr2lib, os, struct

GAME=r"G:/SteamLibrary/steamapps/common/Saints Row 2"
input_idx=[371,1836,1067,454,364,2699,2328,423,1222]
garble='任璨偶巧位雄衡伪该'

def cps_of(data):
    try:
        txt=data.decode('utf-8',errors='replace')
    except: return None
    nums=[int(x) for x in txt.split() if x.strip().isdigit()]
    return nums if len(nums)>500 else None

def test(cps):
    if not cps or len(cps)<max(input_idx)+1: return False
    for idx,gc in zip(input_idx,garble):
        if not (0<=idx<len(cps) and chr(cps[idx])==gc):
            return False
    return True

found=[]
# enumerate all vpp files
for dp,dn,fn in os.walk(GAME):
    for name in fn:
        if name.lower().endswith('.vpp_pc'):
            path=os.path.join(dp,name)
            try:
                v=sr2lib.Vpp(path)
            except Exception:
                continue
            for e in v.entries():
                en=(e['name']+e.get('ext','')).lower()
                if any(k in en for k in ('charlist','charset','ch_','font','chinese','symbol')):
                    data=v.read(e)
                    cps=cps_of(data)
                    if cps and test(cps):
                        found.append((path,en))
                        print(f"*** MATCH *** {path}  {en}  (n={len(cps)})")
                    elif cps:
                        # show a sample mismatch for the first entry of interest
                        pass
print("\nMatches found:", len(found))
if not found:
    print("No charlist in any VPP matches. HUD ordering is not a simple charlist file.")
