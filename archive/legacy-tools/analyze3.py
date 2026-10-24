"""Bucket-structure analysis (corrected): map each hash -> bucket index,
and test candidate bucket functions f(hash) on the OFFICIAL (US) tables.
Also compare CH placement to US placement.
"""
import struct, sys
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
    buckets_info = [struct.unpack_from('<II', d, 12 + b*8) for b in range(buckets)]
    # map pointer LOCATION (off_at + k*4) -> bucket
    loc_bucket = {}
    for b in range(buckets):
        bc, ba = buckets_info[b]
        for k in range(bc):
            loc = ba + k*4
            loc_bucket[loc] = b
    recs = {}; hb = {}
    for k, off in enumerate(ptrs):
        loc = off_at + k*4
        b = loc_bucket.get(loc, -1)
        id1, id2 = struct.unpack_from('<HH', d, off)
        h = (id1<<16)|id2
        recs[h] = off
        hb[h] = b
    return d, recs, hb, buckets, count, off_at, ptrs, buckets_info

def us_decode(d, off):
    i=off+4; out=[]
    while i+2<=len(d):
        v=struct.unpack_from('>H',d,i)[0]
        if v==0: break
        out.append(v); i+=2
    return ''.join(chr(c) for c in out)

for base in ['static','voice_script','platform_pc']:
    us = parse(f'{base}_US'); ch = parse(f'{base}_CH')
    dU,recsU,hbU,nbU,cU,oaU,ptrsU,biU = us
    dC,recsC,hbC,nbC,cC,oaC,ptrsC,biC = ch
    print(f"\n##### {base}: US nb={nbU} count={cU} | CH nb={nbC} count={cC}")
    # bucket usage
    usedU = len(set(hbU.values())); usedC = len(set(hbC.values()))
    print(f"  buckets used: US {usedU}/{nbU}  CH {usedC}/{nbC}")
    # check every hash present in both: does bucket index correspond via a mod function?
    common = set(recsU)&set(recsC)
    # test f(h)=h % nb on US
    okU = sum(1 for h in recsU if h%nbU == hbU[h])
    okC = sum(1 for h in recsC if h%nbC == hbC[h])
    print(f"  h%nb matches bucket: US {okU}/{cU}  CH {okC}/{cC}")
    # test f(h) = (h>>16) % nb
    okU2 = sum(1 for h in recsU if (h>>16)%nbU == hbU[h])
    okC2 = sum(1 for h in recsC if (h>>16)%nbC == hbC[h])
    print(f"  (h>>16)%nb matches: US {okU2}/{cU}  CH {okC2}/{cC}")
    # Examine: are records within a bucket contiguous in hash? sample bucket with most records
    from collections import Counter
    cntU = Counter(hbU.values()); cntC = Counter(hbC.values())
    topb = cntU.most_common(1)[0][0]
    hs_in = sorted(h for h,b in hbU.items() if b==topb)
    print(f"  US biggest bucket #{topb} has {len(hs_in)} hashes; first few: {[hex(x) for x in hs_in[:4]]}")
    # For the SAME hashes, what are CH buckets? see if CH buckets are 'spread' differently
    chb_of_same = [hbC.get(h,-1) for h in hs_in[:10]]
    print(f"  CH buckets for those same 10 hashes: {chb_of_same}")
