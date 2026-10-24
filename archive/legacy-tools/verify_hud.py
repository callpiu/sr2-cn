#!/usr/bin/env python3
# Test hypothesis: the activity HUD maps slot VALUE directly as glyph index
# (i.e. glyph_index = slot, not slot-0x20). Then garble char for a content char
# whose normal slot is S should be charlist_CH[S].
import sr2lib, struct

v = sr2lib.Vpp(r"G:/SteamLibrary/steamapps/common/Saints Row 2/patch.vpp_pc")
ents = {(e['name']+e.get('ext','')).lower():e for e in v.entries()}
cl = v.read(ents['charlist_chtxt'])
codepoints=[int(x) for x in cl.decode('utf-8').split() if x.strip().isdigit()]

# content chars of REC1 with their NORMAL slot (index+0x20)
content = "你的弟兄们需要你的保护"
# find each char's normal index in charlist, then slot = idx+0x20
cp2idx={cp:i for i,cp in enumerate(codepoints)}
print("char  normal_slot  charlist_CH[normal_slot]  garble_expected")
mapping = {'你':'任','的':'璨','弟':'偶','兄':'巧','们':'位','需':'雄','要':'衡','保':'伪','护':'该'}
for ch in content:
    idx=cp2idx[ord(ch)]
    slot=idx+0x20
    # HUD hypothesis: displays charlist_CH[slot]
    hud_char = chr(codepoints[slot]) if slot < len(codepoints) else '?'
    print(f"  {ch}    {slot:5d}        {hud_char}                  {mapping.get(ch,'?')}")

# Check match
allmatch = all((chr(codepoints[cp2idx[ord(ch)]+0x20]) == mapping[ch]) for ch in mapping)
print("\nALL MATCH (HUD uses glyph_index = slot, no -0x20):", allmatch)

# Also test the alternate hypothesis: glyph_index = slot - 0x20 but with a
# DIFFERENT charlist offset? If glyph_index=slot-0x20 gives the CORRECT char,
# that's the normal path (which would NOT be garbled). Show it for contrast.
print("\ncontrast: normal decode glyph_index=slot-0x20 ->")
for ch in content:
    idx=cp2idx[ord(ch)]
    print(f"  {ch} -> {chr(codepoints[idx])}")
