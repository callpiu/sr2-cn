"""diag14: compare patch vs common fnt_chinese.vf3_pc glyph position arrays.
Also test whether either font's pos array reproduces the in-game screen mapping
for REC1 (slot -> screen charlist idx)."""
import sys, struct
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

PATCH = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
COMMON = r'G:\SteamLibrary\steamapps\common\Saints Row 2\common.vpp_pc'

patch = Vpp(PATCH)
common = Vpp(COMMON)

def get_vf3(vp, name):
    e = vp.find(name, 'vf3_pc')
    if e is None:
        # search
        for x in vp.entries():
            if x['name'].lower() == name.lower():
                e = x; break
    return vp.read(e), e['size']

pb, psz = get_vf3(patch, 'fnt_chinese')
cb, csz = get_vf3(common, 'fnt_chinese')
print('patch vf3 size', psz, 'common vf3 size', csz)

def nfnt(buf):
    assert buf[:4] == b'VFNT'
    return struct.unpack_from('<I', buf, 8)[0]
Np = nfnt(pb); Nc = nfnt(cb)
print('patch N =', Np, 'common N =', Nc)

# The tail after 0xD0 + N*16 holds glyph position arrays.
# Try to locate U/V arrays. Search for a u16 array of length N within the tail
# whose values look like cell indices (0..2048) and which is "sorted-ish" or
# matches a spacing pattern.  We'll just dump the tail and look for the arrays
# at the documented offsets and also scan.
def candidates(buf, N):
    out = {}
    # documented offsets
    for off in (0xAF6C, 0xDB18):
        if off + N*2 <= len(buf):
            arr = list(struct.unpack_from('<%dH' % N, buf, off))
            out['off%X' % off] = arr
    # brute scan for u16 arrays where all values in [0,2048] and the array is
    # "plausible" (we just collect a few candidates with low variance of range)
    n = len(buf)
    hits = []
    for off in range(0xD0, n - N*2, 2):
        arr = struct.unpack_from('<%dH' % N, buf, off)
        mx = max(arr); mn = min(arr)
        if mx <= 2048 and mn >= 0:
            # heuristic: fraction of distinct values
            if len(set(arr)) > N*0.5:
                hits.append((off, mx, mn, len(set(arr))))
    return out, hits

po, ph = candidates(pb, Np)
print('patch documented arrays present:', list(po.keys()))
print('patch brute hits (off,max,min,distinct):', ph[:10])
co, ch = candidates(cb, Nc)
print('common documented arrays present:', list(co.keys()))
print('common brute hits:', ch[:10])

# Try to match REC1 screen mapping against any candidate array in either font.
# REC1 slot -> screen charlist idx (reliable, 9 distinct pairs):
rec1_pairs = {371:336, 1836:1784, 1035:410, 422:967, 332:362,
              2667:2656, 2296:2268, 391:354, 1190:2342}
def try_match(buf, N):
    n = len(buf)
    for off in range(0xD0, n - N*2, 2):
        arr = struct.unpack_from('<%dH' % N, buf, off)
        ok = all(idx < N and arr[idx] == sv for idx, sv in rec1_pairs.items())
        if ok:
            return off
    return None

m_patch = try_match(pb, Np)
m_common = try_match(cb, Nc)
print('REC1 mapping matches patch array at offset:', m_patch)
print('REC1 mapping matches common array at offset:', m_common)

# Also try as u32
def try_match_u32(buf, N):
    n = len(buf)
    for off in range(0xD0, n - N*4, 4):
        arr = struct.unpack_from('<%dI' % N, buf, off)
        if all(idx < N and (arr[idx] & 0xFFFF) == sv for idx, sv in rec1_pairs.items()):
            return off
    return None
print('REC1 u32 match patch:', try_match_u32(pb, Np), 'common:', try_match_u32(cb, Nc))
