"""Confirm rebuilt CH blobs preserve the ORIGINAL CH text byte-for-byte,
and (best-effort) decode via charlist to show human-readable Chinese.
"""
import struct, sys, re
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

GAMEP = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
vpp = Vpp(GAMEP)

def ch_text_map(name):
    e = vpp.find(name, 'le_strings')
    d = vpp.read(e)
    magic, ver, buckets, count = struct.unpack_from('<IHHI', d, 0)
    off_at = 12 + buckets*8
    ptrs = [struct.unpack_from('<I', d, off_at + k*4)[0] for k in range(count)]
    m = {}
    for off in ptrs:
        id1,id2 = struct.unpack_from('<HH', d, off)
        h = (id1<<16)|id2
        i = off+4
        while i+2 <= len(d):
            v = struct.unpack_from('>H', d, i)[0]
            if v == 0: break
            i += 2
        if h not in m:
            m[h] = d[off+4:i]
    return m

def load_rebuilt(path):
    d = open(path,'rb').read()
    magic, ver, buckets, count = struct.unpack_from('<IHHI', d, 0)
    off_at = 12 + buckets*8
    ptrs = [struct.unpack_from('<I', d, off_at + k*4)[0] for k in range(count)]
    recs = {}
    for off in ptrs:
        id1,id2 = struct.unpack_from('<HH', d, off)
        h = (id1<<16)|id2
        i = off+4
        while i+2 <= len(d):
            v = struct.unpack_from('>H', d, i)[0]
            if v == 0: break
            i += 2
        recs[h] = d[off+4:i]
    return recs

# charlist (best-effort)
body = None
try:
    ce = vpp.find('charlist_CH', 'txt')
    ctxt = vpp.read(ce)
    mm = re.search(rb'count=(\d+)', ctxt)
    if mm:
        start = mm.end()
        end = ctxt.find(b'//ENDOFFILE')
        if end < 0: end = len(ctxt)
        body = [int(x) for x in re.findall(rb'\d+', ctxt[start:end])]
        print(f"charlist_CH: {len(body)} codepoints")
    else:
        print("charlist_CH: no 'count=' header found; skip decode")
except Exception as ex:
    print(f"charlist load failed: {ex}")

def decode(d):
    if body is None: return None
    out=[]
    for v in struct.unpack_from('>%dH'%(len(d)//2), d, 0) if False else []:
        pass
    i=0
    while i+2<=len(d):
        v=struct.unpack_from('>H',d,i)[0]
        if v==0: break
        if v<0x100: out.append(chr(v))
        else:
            idx=v-0x20
            out.append(chr(body[idx]) if 0<=idx<len(body) else '?')
        i+=2
    return ''.join(out)

for name, path in [('static_CH', r'F:\sr2-cn\_rebuilt\static_CH.le_strings'),
                   ('voice_script_CH', r'F:\sr2-cn\_rebuilt\voice_script_CH.le_strings')]:
    orig = ch_text_map(name)
    reb = load_rebuilt(path)
    # byte-for-byte comparison
    mism = [h for h in orig if h in reb and orig[h] != reb[h]]
    only_orig = [h for h in orig if h not in reb]
    only_reb = [h for h in reb if h not in orig]
    print(f"\n=== {name} ===  orig={len(orig)} rebuilt={len(reb)}")
    print(f"  text-byte mismatches vs original CH: {len(mism)}")
    print(f"  hashes only in original: {len(only_orig)} | only in rebuilt: {len(only_reb)}")
    for h in (0x73004296, 0x84F287ED):
        if h in reb:
            dec = decode(reb[h])
            print(f"  {h:#010x}: {dec!r}" if dec else f"  {h:#010x}: (decode n/a) bytes={reb[h][:20].hex()}")
        else:
            print(f"  {h:#010x}: NOT PRESENT in rebuilt")
    # a couple samples
    for h in list(reb)[:3]:
        dec = decode(reb[h])
        print(f"    sample {h:#010x}: {dec!r}" if dec else f"    sample {h:#010x}: bytes={reb[h][:20].hex()}")
