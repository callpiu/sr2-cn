#!/usr/bin/env python3
# Locate the common Chinese font's per-glyph coordinate arrays (U/V) and atlas,
# then verify: does common-font glyph index 371 render as 任 (ren) or 你 (ni)?
# That tells us which font/charlist the activity HUD uses.
import sr2lib, struct, numpy as np

GAME=r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def find_uv(vf3):
    # scan for an i32 array of length N (=count) whose values look like atlas coords
    count=struct.unpack_from('<I', vf3, 8)[0]
    print("  font count:", count)
    cand=[]
    for off in range(0xD0, len(vf3)-count*4, 4):
        # quick check: read first 4 values within atlas range
        vals=struct.unpack_from('<%di'%min(count,8), vf3, off)
        if all(0<=v<2048 for v in vals):
            # verify whole array plausible
            arr=struct.unpack_from('<%di'%count, vf3, off)
            if all(0<=v<2048 for v in arr):
                cand.append(off)
    return count, cand

vpatch=sr2lib.Vpp(GAME+r"/patch.vpp_pc")
pe={(e['name']+e.get('ext','')).lower():e for e in vpatch.entries()}
patch_vf3=vpatch.read(pe['fnt_chinesevf3_pc'])
print("patch vf3 size", len(patch_vf3))
pc, pcand=find_uv(patch_vf3)
print("  patch U/V candidate offsets:", [hex(o) for o in pcand[:6]])

vcommon=sr2lib.Vpp(GAME+r"/common.vpp_pc")
ce={(e['name']+e.get('ext','')).lower():e for e in vcommon.entries()}
common_vf3=vcommon.read(ce['fnt_chinesevf3_pc'])
print("common vf3 size", len(common_vf3))
cc, ccand=find_uv(common_vf3)
print("  common U/V candidate offsets:", [hex(o) for o in ccand[:6]])

# Load atlases
atlasA = vpatch.read(pe['fnt_chineseg_peg_pc']) if 'fnt_chineseg_peg_pc' in pe else None
pa={(e['name']+e.get('ext','')).lower():e for e in vpatch.entries()}
print("patch atlas entries:", [k for k in pa if 'fnt' in k or 'peg' in k])
ta={(e['name']+e.get('ext','')).lower():e for e in sr2lib.Vpp(GAME+r"/textures.vpp_pc").entries()}
print("textures atlas entries w/ fnt:", [k for k in ta if 'fnt' in k])
