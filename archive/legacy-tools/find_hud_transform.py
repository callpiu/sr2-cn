#!/usr/bin/env python3
import sr2lib
v=sr2lib.Vpp(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
pe={(e['name']+e.get('ext','')).lower():e for e in v.entries()}
cl=v.read(pe['charlist_chtxt'])
cps=[int(x) for x in cl.decode('utf-8').split() if x.strip().isdigit()]
cp2i={cp:i for i,cp in enumerate(cps)}

input_idx=[371,1836,1067,454,364,2699,2328,423,1222]
garble='任璨偶巧位雄衡伪该'
print("char  input_idx  garble  garble_idx_in_CH  delta(idx-gi)  slot")
for idx,gc in zip(input_idx,garble):
    gi=cp2i[ord(gc)]
    print(f"  {gc}    {idx:5d}      {gc}     {gi:5d}            {idx-gi:5d}        {idx+0x20}")

# test candidate linear transforms on the patch charlist:
# hypothesis: HUD shows CH[ a*idx + b ]  (idx = slot-0x20)  OR  CH[ a*slot + b ]
print("\nTry linear transform idx -> a*idx+b within patch charlist:")
import itertools
best=None
for a in (1,):
    for b in range(-50,51):
        ok=True
        for idx,gc in zip(input_idx,garble):
            j=idx*a+b
            if not (0<=j<len(cps) and cps[j]==ord(gc)):
                ok=False; break
        if ok:
            print(f"  FOUND CH[ idx + {b} ] works")
# also try slot-based
print("Try CH[ (slot)+b ]:")
for b in range(-50,51):
    ok=True
    for idx,gc in zip(input_idx,garble):
        j=(idx+0x20)+b
        if not (0<=j<len(cps) and cps[j]==ord(gc)):
            ok=False; break
    if ok:
        print(f"  FOUND CH[ slot + {b} ] works")
