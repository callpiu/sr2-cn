#!/usr/bin/env python3
# Fully parse static_CH.le_strings, decode each record via charlist_chtxt,
# and find ALL records containing the activity text (duplicate-record trap).
import sr2lib, struct

GAME = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = sr2lib.Vpp(GAME + r"/patch.vpp_pc")
ents = {(e['name']+e.get('ext','')).lower():e for e in v.entries()}

def parse_le_strings(data):
    # header: magic(4) ver(u16) buckets(u16) count(u32) = 12 bytes
    magic = data[:4]
    ver, buckets, count = struct.unpack_from("<HHI", data, 4)
    off = 12
    # bucket table: buckets * (cnt u32, addr u32)
    buckets_arr = []
    for i in range(buckets):
        cnt, addr = struct.unpack_from("<II", data, off); off += 8
        buckets_arr.append((cnt, addr))
    # pointer array: count * u32 (absolute record offsets)
    ptrs = []
    for i in range(count):
        p = struct.unpack_from("<I", data, off)[0]; off += 4
        ptrs.append(p)
    # parse each record
    recs = []
    for p in ptrs:
        if p == 0 or p >= len(data): 
            recs.append(None); continue
        id1, id2 = struct.unpack_from("<HH", data, p)
        q = p+4
        slots=[]; ok=True
        while q+2 <= len(data):
            w = struct.unpack_from(">H", data, q)[0]
            if w == 0: break
            slots.append(w); q += 2
        recs.append((id1, id2, slots))
    return recs

# charlist
cl = ents['charlist_chtxt']
cld = v.read(cl)
print("charlist_chtxt size", len(cld), "first bytes:", cld[:40])
# try decode as utf-8 / utf-16
for enc in ("utf-8","utf-16-le","utf-16-be"):
    try:
        txt = cld.decode(enc)
        print(f"  {enc}: {txt[:30]!r}")
    except Exception as e:
        print(f"  {enc} fail {e}")

st = ents['static_chle_strings']
std = v.read(st)
recs = parse_le_strings(std)
print("static_CH records:", len(recs))

# decode slot -> char using charlist if it's a simple char list
# Build char list: assume charlist_chtxt is a list of chars (try utf-8 after stripping)
chars = None
for enc in ("utf-8","utf-16-le","utf-16-be"):
    try:
        t = cld.decode(enc)
        if len(t) > 1000:
            chars = t; break
    except: pass
print("charlist len:", len(chars) if chars else None)

def dec(slots):
    out=[]
    for w in slots:
        if w < 0x20:
            out.append(f"<{w:02X}>")
        else:
            idx = w - 0x20
            if chars and 0 <= idx < len(chars):
                out.append(chars[idx])
            else:
                out.append(f"[{w}]")
    return "".join(out)

# Find records containing 弟兄 / 保护 / 袭击 / homies-related
hits=[]
for i,r in enumerate(recs):
    if r is None: continue
    id1,id2,slots=r
    s=dec(slots)
    if ('弟兄' in s) or ('保护' in s) or ('袭击' in s) or ('生意' in s):
        h=(id1<<16)|id2
        hits.append((i,h,s))
print("="*70)
print("Records mentioning 弟兄/保护/袭击/生意:", len(hits))
for i,h,s in hits:
    print(f"  rec#{i} hash {h:08X}: {s[:80]}")
