#!/usr/bin/env python3
# Properly decode static_CH records using charlist_chtxt (code-point list, one per line).
import sr2lib, struct

GAME = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = sr2lib.Vpp(GAME + r"/patch.vpp_pc")
ents = {(e['name']+e.get('ext','')).lower():e for e in v.entries()}

# charlist codepoints
cl = v.read(ents['charlist_chtxt'])
cps=[]
for x in cl.decode('utf-8').split():
    x=x.strip()
    if x.isdigit(): cps.append(int(x))
codepoints = cps
print("codepoints:", len(codepoints), "first:", codepoints[:10])

def parse_le_strings(data):
    ver, buckets, count = struct.unpack_from("<HHI", data, 4)
    off = 12
    for i in range(buckets): off += 8
    ptrs=[]; 
    for i in range(count):
        ptrs.append(struct.unpack_from("<I", data, off)[0]); off+=4
    recs=[]
    for p in ptrs:
        if p==0 or p>=len(data): recs.append(None); continue
        id1,id2=struct.unpack_from("<HH",data,p)
        q=p+4; slots=[]
        while q+2<=len(data):
            w=struct.unpack_from(">H",data,q)[0]
            if w==0: break
            slots.append(w); q+=2
        recs.append((id1,id2,slots))
    return recs

st=v.read(ents['static_chle_strings'])
recs=parse_le_strings(st)
print("records:", len(recs))

def dec(slots):
    out=[]
    for w in slots:
        if w<0x20: out.append(f"<{w:02X}>")
        else:
            idx=w-0x20
            if 0<=idx<len(codepoints):
                try: out.append(chr(codepoints[idx]))
                except: out.append(f"[{w}]")
            else: out.append(f"[{w}]")
    return "".join(out)

# sanity: decode the REC1/REC2 known offsets
known=[(0x84F287ED,"REC1"),(0x10AF1E62,"REC2")]
for h,name in known:
    for r in recs:
        if r and (r[0]<<16|r[1])==h:
            print(f"\n{name} {h:08X}: {dec(r[2])}")
            break

# search all records for distinctive surviving substrings
targets=["保护","车耐久","谈几笔生意","生意","袭击","弟兄"]
from collections import defaultdict
found=defaultdict(list)
for i,r in enumerate(recs):
    if r is None: continue
    s=dec(r[2])
    for t in targets:
        if t in s:
            found[t].append((i, r[0]<<16|r[1], s))
print("\n=== hits ===")
for t in targets:
    print(f"\n## '{t}': {len(found[t])} records")
    for i,h,s in found[t][:10]:
        print(f"   #{i} {h:08X}: {s[:90]}")
