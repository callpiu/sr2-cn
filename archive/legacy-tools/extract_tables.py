#!/usr/bin/env python3
# Extract the activity record (hash 84F287ED / 10AF1E62) from static_CH,
# platform_pc_CH, voice_script_CH inside patch.vpp_pc, and compare raw slot streams.
import sr2lib, struct

GAME = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
VP = GAME + r"/patch.vpp_pc"
v = sr2lib.Vpp(VP)
ents = { (e['name']+e.get('ext','')).lower(): e for e in v.entries() }

def find_record_slotstream(data, h):
    id1 = (h>>16)&0xFFFF; id2 = h&0xFFFF
    pat = struct.pack("<HH", id1, id2)
    idx = data.find(pat)
    if idx < 0:
        return None
    # slot stream starts at idx+4, u16 BE, ends at 0x0000
    off = idx+4
    stream=[]; p=off
    while p+2 <= len(data):
        w = struct.unpack_from(">H", data, p)[0]
        if w == 0:
            break
        stream.append(w); p+=2
    return idx, stream, data[idx:p+2]

for tbl in ["static_CHle_strings","platform_pc_CHle_strings","voice_script_CHle_strings"]:
    e = ents.get(tbl.lower())
    if not e:
        print("MISSING", tbl); continue
    data = v.read(e)
    print("="*60)
    print(tbl, "size", len(data))
    for h,name in [(0x84F287ED,"REC1"),(0x10AF1E62,"REC2")]:
        r = find_record_slotstream(data, h)
        if not r:
            print(f"  {name} 84F287ED/10AF1E62: NOT FOUND")
            continue
        idx, stream, raw = r
        # render slot->? we just show counts + raw hex of first 40 u16
        ctrl = sum(1 for w in stream if w<0x20)
        print(f"  {name} @off {idx}  nslots={len(stream)} ctrl={ctrl}")
        print(f"     first 30 slots: {stream[:30]}")
