"""Definitive le_strings hash-set comparison.

Correct reader (verified empirically):
  header: magic u32 | ver u16 | buckets u16 | count u32   (12 bytes)
  buckets: buckets * (count u32, addr u32)                (8 bytes each)
  ptrs:    count * u32   absolute file offsets
  record@ptr: [id1 LE u16][id2 LE u16][UTF-16BE units...][0x0000]
              hash = (id1<<16)|id2 ; text starts at ptr+4
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
    assert magic == MAGIC, (name, hex(magic))
    off_at = 12 + buckets*8
    ptrs = [struct.unpack_from('<I', d, off_at + k*4)[0] for k in range(count)]
    recs = {}          # hash -> list of offsets (allow dups)
    dup = 0
    for off in ptrs:
        if not (0 < off <= len(d)-6):
            continue
        id1, id2 = struct.unpack_from('<HH', d, off)
        h = (id1 << 16) | id2
        # sanity: text must be valid series of BE u16 ending 0x0000 within bounds
        i = off+4
        ok = True
        while i+2 <= len(d):
            v = struct.unpack_from('>H', d, i)[0]
            if v == 0:
                break
            i += 2
        else:
            ok = False
        if ok:
            recs.setdefault(h, []).append(off)
            if len(recs[h]) > 1:
                dup += 1
    return d, recs, dup, count

def us_text(d, off):
    """Decode a US/other-language record's text as direct UTF-16BE code units."""
    i = off+4
    out = []
    while i+2 <= len(d):
        v = struct.unpack_from('>H', d, i)[0]
        if v == 0:
            break
        out.append(v); i += 2
    try:
        return ''.join(chr(c) for c in out)
    except Exception:
        return repr(out[:20])

def ch_text(d, off):
    """Decode a CH record: <0x100 literal, >=0x100 -> charlist slot (needs cl)."""
    i = off+4
    out = []
    while i+2 <= len(d):
        v = struct.unpack_from('>H', d, i)[0]
        if v == 0:
            break
        out.append(v); i += 2
    return out   # return slot list; caller maps via charlist

# ---- parse the four core tables ----
SU = parse('static_US');  SC = parse('static_CH')
VU = parse('voice_script_US'); VC = parse('voice_script_CH')

print("table            nbuckets count  parsed  dups")
for nm,(d,recs,dup,cnt) in [('static_US',SU),('static_CH',SC),('voice_script_US',VU),('voice_script_CH',VC)]:
    print(f"  {nm:17s} {struct.unpack_from('<H',d,6)[0]:5d}  {cnt:6d}  {len(recs):6d}  {dup}")

# ---- STATIC: US hashes missing in CH ----
us_hashes = set(SU[1]); ch_hashes = set(SC[1])
missing_static = sorted(us_hashes - ch_hashes)
extra_static   = sorted(ch_hashes - us_hashes)
print(f"\n=== STATIC ===  US={len(us_hashes)} CH={len(ch_hashes)}")
print(f"  hashes in US but MISSING in CH: {len(missing_static)}")
print(f"  hashes in CH but not in US (CH-only): {len(extra_static)}")
print("\n  -- US-only / missing-in-CH (these can trigger the fallback) --")
for h in missing_static:
    off = SU[1][h][0]
    print(f"    {h:#010x}  {us_text(SU[0], off)!r}")

# ---- VOICE: US hashes missing in CH ----
vu_hashes = set(VU[1]); vc_hashes = set(VC[1])
missing_voice = sorted(vu_hashes - vc_hashes)
extra_voice   = sorted(vc_hashes - vu_hashes)
print(f"\n=== VOICE_SCRIPT ===  US={len(vu_hashes)} CH={len(vc_hashes)}")
print(f"  hashes in US but MISSING in CH: {len(missing_voice)}")
print(f"  hashes in CH but not in US (CH-only): {len(extra_voice)}")
print("\n  -- US-only / missing-in-CH --")
for h in missing_voice:
    off = VU[1][h][0]
    print(f"    {h:#010x}  {us_text(VU[0], off)!r}")
