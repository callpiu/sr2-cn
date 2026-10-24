"""diag20: how many static_CH / voice_script_CH entries exist in the LIVE
patch.vpp_pc, where does each point, and what do the two homies hashes decode
to in EACH le_strings blob physically present in the file (incl. orphaned
appended copies). Determines whether the subtitle could be reading an orphaned
old blob instead of my experiment blob."""
import sys, struct
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

P = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
patch = Vpp(P)
data = patch.data
CPS = [int(x) for x in patch.read(patch.find('charlist_CH', 'txt')).decode('ascii','replace').split('//ENDOFFILE')[0].split() if x.isdigit()]

def dec(units):
    out=[]
    for u in units:
        if u<0x80: out.append(chr(u))
        else:
            i=u-0x20; out.append(chr(CPS[i]) if 0<=i<len(CPS) else '?')
    return ''.join(out)

def parse_blob(d):
    """parse a le_strings blob -> dict hash->text, or None"""
    try:
        magic,ver,nb,count = struct.unpack_from('<IHHI', d, 0)
    except struct.error:
        return None
    if magic != 0xA84C7F73: return None
    if not (0 < nb < 100000 and 0 < count < 200000): return None
    A0 = 12 + nb*8
    if A0 + count*4 > len(d): return None
    recs={}
    ok=True
    for k in range(count):
        off = struct.unpack_from('<I', d, A0+k*4)[0]
        if not (0 < off <= len(d)-6): ok=False; break
        id1,id2 = struct.unpack_from('<HH', d, off)
        h=(id1<<16)|id2
        o=off+4; units=[]
        while o+2<=len(d):
            u=struct.unpack_from('>H',d,o)[0]; o+=2
            if u==0: break
            units.append(u)
        if h not in recs: recs[h]=dec(units)
    if not ok: return None
    return recs, nb, count

TARGETS = {0x84F287ED, 0x10AF1E62}

# 1) entries named static_CH / voice_script_CH
print('=== entries named static_CH / voice_script_CH ===')
for e in patch.entries():
    if e['name'].lower() in ('static_ch','voice_script_ch'):
        blob = patch.read(e)
        r = parse_blob(blob)
        t = {h: r[0].get(h) for h in TARGETS} if r else None
        print('%-18s body_off=%d size=%d -> %s' % (e['name'], patch.data_start+e['body'], e['size'], t))

# 2) scan whole file for every le_strings blob containing the target hashes
print('\n=== all le_strings blobs physically present containing a target hash ===')
MAGIC = bytes.fromhex('737fc8a8')  # 0xA84C7F73 LE
i = 0; found = 0
n = len(data)
while True:
    j = data.find(MAGIC, i)
    if j < 0: break
    i = j + 1
    # try to parse a blob starting here
    try:
        magic,ver,nb,count = struct.unpack_from('<IHHI', data, j)
    except struct.error:
        continue
    if not (0 < nb < 100000 and 0 < count < 200000):
        continue
    A0 = 12 + nb*8
    if A0 + count*4 > n - j:
        continue
    # quick: read a few pointers, sanity
    recs={}; ok=True
    for k in range(count):
        off = struct.unpack_from('<I', data, j+A0+k*4)[0]
        if not (j+0 < off <= n-6) or off < j:  # offset should be within this blob region
            # offsets are absolute to blob start j
            if not (0 < off <= (n-j)-6):
                ok=False; break
        if off < A0 + count*4:  # pointer into header region = bogus
            ok=False; break
        id1,id2 = struct.unpack_from('<HH', data, j+off)
        h=(id1<<16)|id2
        if h in TARGETS and h not in recs:
            o=j+off+4; units=[]
            while o+2<=n:
                u=struct.unpack_from('>H',data,o)[0]; o+=2
                if u==0: break
                units.append(u)
            recs[h]=dec(units)
    if ok and any(h in recs for h in TARGETS):
        found += 1
        print('blob@file_off=%d nb=%d count=%d  %s' % (j, nb, count, {hex(h):recs[h] for h in TARGETS if h in recs}))
print('total blobs with a target hash:', found)
