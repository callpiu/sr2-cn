"""Deploy the rebuilt static_CH / voice_script_CH into the game patch.vpp_pc.
Backs up current file first, injects rebuilt blobs (append+repoint), saves, and
reports the new md5 (v532)."""
import struct, sys, os, shutil, hashlib
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

GAMEP = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
STAGE = r'F:\sr2-cn\_rebuilt'
MAGIC = 0xA84C7F73

def md5(path):
    return hashlib.md5(open(path,'rb').read()).hexdigest()

# 0) confirm current md5 (expect v531 = 7a30500e)
cur = md5(GAMEP)
print(f"current game patch md5 = {cur}  (expected v531 7a30500e)")

# 1) backup
bak = GAMEP + '.v531_before_mirror.bak'
if not os.path.exists(bak):
    shutil.copy(GAMEP, bak)
    print(f"backup -> {bak}  ({md5(bak)})")
else:
    print(f"backup exists already: {bak}")

# 2) inject
vpp = Vpp(GAMEP)
for ch_n, fname in [('static_CH','static_CH.le_strings'),
                    ('voice_script_CH','voice_script_CH.le_strings')]:
    blob = open(os.path.join(STAGE, fname),'rb').read()
    ent = vpp.find(ch_n, 'le_strings')
    vpp.replace_body_appended(ent, blob, align=0x800)
    print(f"  injected {ch_n}: {len(blob)} bytes")

# 3) save
vpp.save(GAMEP)
newmd5 = md5(GAMEP)
print(f"saved -> {GAMEP}")
print(f"NEW md5 (v532) = {newmd5}")

# 4) quick sanity re-parse of the two entries in the live file
v2 = Vpp(GAMEP)
for ch_n in ['static_CH','voice_script_CH']:
    d = v2.read(v2.find(ch_n,'le_strings'))
    magic,ver,nb,count = struct.unpack_from('<IHHI', d, 0)
    off_at = 12 + nb*8
    ptrs = [struct.unpack_from('<I', d, off_at+k*4)[0] for k in range(count)]
    bi = [struct.unpack_from('<II', d, 12+b*8) for b in range(nb)]
    used = set()
    for b in range(nb):
        bc,ba = bi[b]
        for k in range(bc):
            used.add(b)
    print(f"  LIVE {ch_n}: nb={nb} count={count} buckets_used={len(used)}/{nb}  ok={magic==MAGIC}")
