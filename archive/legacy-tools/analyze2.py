"""Deep analysis:
  (A) compare EVERY *_US vs *_CH language table for missing hashes
  (B) scan voice_script_CH for corrupt records (out-of-range slots)
  (C) reverse-engineer the bucket-index function f from US tables
"""
import struct, sys, collections
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

P = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
vpp = Vpp(P)
MAGIC = 0xA84C7F73

def parse(name):
    e = vpp.find(name, 'le_strings')
    d = vpp.read(e)
    magic, ver, buckets, count = struct.unpack_from('<IHHI', d, 0)
    assert magic == MAGIC
    off_at = 12 + buckets*8
    ptrs = [struct.unpack_from('<I', d, off_at + k*4)[0] for k in range(count)]
    # bucket table: (count, addr) ; addr = absolute file offset of first pointer of bucket
    buckets_info = [struct.unpack_from('<II', d, 12 + b*8) for b in range(buckets)]
    recs = {}          # hash -> offset
    hash_to_bucket = {}# hash -> bucket index
    # assign each pointer to its bucket by addr range
    for b in range(buckets):
        bc, ba = buckets_info[b]
        # pointers belonging to bucket b are at file offsets [ba, ba+bc*4)
        pass
    # simpler: walk bucket table in order, the k-th pointer overall belongs to bucket determined by addr intervals
    # Build pointer->bucket by scanning addr intervals
    interval = []
    for b in range(buckets):
        bc, ba = buckets_info[b]
        interval.append((ba, ba+bc*4, b))
    interval.sort()
    ptr_bucket = {}
    for k, off in enumerate(ptrs):
        for (s,e,b) in interval:
            if s <= off < e:
                ptr_bucket[k] = b
                break
    for k, off in enumerate(ptrs):
        id1, id2 = struct.unpack_from('<HH', d, off)
        h = (id1<<16)|id2
        recs[h] = off
        hash_to_bucket[h] = ptr_bucket.get(k, -1)
    return d, recs, hash_to_bucket, buckets, count

def raw_text(d, off):
    i = off+4
    start = i
    while i+2 <= len(d):
        v = struct.unpack_from('>H', d, i)[0]
        if v == 0:
            break
        i += 2
    return d[start:i]   # includes no terminator

def us_decode(d, off):
    i = off+4; out=[]
    while i+2 <= len(d):
        v = struct.unpack_from('>H', d, i)[0]
        if v==0: break
        out.append(v); i+=2
    return ''.join(chr(c) for c in out)

# ---- (A) compare all tables ----
langs = ['static','voice_script','platform_pc']
print("=== (A) missing-hash comparison (US hash present, CH absent) ===")
for base in langs:
    us = parse(f'{base}_US'); ch = parse(f'{base}_CH')
    us_h = set(us[1]); ch_h = set(ch[1])
    miss = sorted(us_h - ch_h)
    extra = sorted(ch_h - us_h)
    print(f"  {base:14s} US={len(us_h)} CH={len(ch_h)}  missing_in_CH={len(miss)}  CH_only={len(extra)}")
    for h in miss[:40]:
        print(f"      MISS {h:#010x}  US={us_decode(us[0], us[1][h])!r}")

# ---- (B) scan voice_script_CH for corrupt records ----
print("\n=== (B) corrupt-record scan in voice_script_CH ===")
d,recs,hb,nb,count = parse('voice_script_CH')
# charlist length unknown here; use a generous bound: valid slot < 0x100 or < 20000+0x20
MAXSLOT = 20000 + 0x20
corrupt=[]
for h,off in recs.items():
    units=[]; i=off+4; ok=True
    while i+2 <= len(d):
        v=struct.unpack_from('>H',d,i)[0]
        if v==0: break
        units.append(v); i+=2
    if any((v<0x100) or (0x100<=v<MAXSLOT) for v in units):
        # need all valid
        if not all((v<0x100) or (0x100<=v<MAXSLOT) for v in units):
            corrupt.append((h,off,units))
    else:
        corrupt.append((h,off,units))
print(f"  voice_script_CH records={count}, suspicious/garbled={len(corrupt)}")
for h,off,units in corrupt[:10]:
    print(f"    hash={h:#010x} off={off:#x} nunits={len(units)} sample={units[:12]}")

# ---- (C) reverse-engineer f from static_US ----
print("\n=== (C) bucket-function search on static_US ===")
d,recs,hb,nb,count = parse('static_US')
pairs = list(hb.items())   # (hash, bucket)
print(f"  static_US nb={nb}, sample pairs (hash->bucket): {pairs[:5]}")
# candidate functions g(h) -> bucket-in-[0,nb). We need g(h) == bucket for all.
import random
def test(fn, name):
    ok=sum(1 for h,b in pairs if fn(h)%nb == b)
    print(f"    {name:28s} match={ok}/{len(pairs)} ({100*ok/len(pairs):.1f}%)")
test(lambda h: h, "h")
test(lambda h: h>>16, "h>>16")
test(lambda h: h & 0xFFFF, "h&0xFFFF")
test(lambda h: (h>>16)^(h&0xFFFF), "(h>>16)^(h&0xFFFF)")
test(lambda h: (h>>16)+(h&0xFFFF), "(h>>16)+(h&0xFFFF)")
test(lambda h: ((h>>16)+(h&0xFFFF))&0xFFFF, "low16 of sum")
test(lambda h: (h*2654435761) & 0xFFFFFFFF, "h*Knuth")
# try high/low byte combos
test(lambda h: ((h>>24)^(h>>16)^(h>>8)^(h&0xFF))&0xFFFF, "xor bytes")
# maybe bucket = (h mod nb) but with h being the ORIGINAL volition string hash not equal to stored id
# We only have stored id. Try treating id1,id2 swapped:
test(lambda h: ((h&0xFFFF)<<16)|(h>>16), "byteswapped h")

# correlation: for buckets, are records sorted? check bucket 0 hashes range
b0 = [h for h,b in pairs if b==0]
print(f"  bucket0 has {len(b0)} hashes; min/max/id example: {b0[:3]} ... {b0[-3:] if b0 else []}")
print(f"  total buckets used: {len(set(b for _,b in pairs))}/{nb}")
