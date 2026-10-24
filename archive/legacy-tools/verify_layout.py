"""Empirically verify the le_strings record byte layout in the deployed patch.vpp_pc."""
import struct, sys
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp

P = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
vpp = Vpp(P)

# list le_strings entries
ents = [e for e in vpp.entries() if e['ext'].lower() == 'le_strings']
print("le_strings entries:")
for e in ents:
    print(f"  {e['name']}.{e['ext']}  size={e['size']}")

def dump(tname):
    e = vpp.find(tname, 'le_strings')
    d = vpp.read(e)
    magic, ver, buckets, count = struct.unpack_from('<IHHI', d, 0)
    print(f"\n=== {tname} === magic={magic:#010x} ver={ver} buckets={buckets} count={count} filesize={len(d)}")
    off_at = 12 + buckets*8
    # first bucket addr
    b0c, b0a = struct.unpack_from('<II', d, 12)
    print(f"  header=12  off_at(12+nb*8)={off_at}  bucket0 (count={b0c}, addr={b0a})  A0_check={off_at} vs first ptr region")
    ptrs = [struct.unpack_from('<I', d, off_at + k*4)[0] for k in range(count)]
    print(f"  first 5 pointers: {ptrs[:5]}")
    for off in ptrs[:3]:
        seg = d[off:off+40]
        print(f"  off={off:#x} bytes: {seg.hex()}")
        # try decode assuming ID at off (4 bytes), text at off+4
        id1, id2 = struct.unpack_from('<HH', d, off)
        h = (id1<<16)|id2
        # read units at off+4
        units=[]
        i=off+4
        while i+2<=len(d):
            v=struct.unpack_from('>H', d, i)[0]
            if v==0: break
            units.append(v); i+=2
        txt=''.join(chr(c) if c<0x100 else f'<{c}>' for c in units[:20])
        print(f"     ID=(id1={id1},id2={id2}) hash={h:#010x}  text@off+4: {txt}")
        # also try text at off+8
        units2=[]
        i=off+8
        while i+2<=len(d):
            v=struct.unpack_from('>H', d, i)[0]
            if v==0: break
            units2.append(v); i+=2
        txt2=''.join(chr(c) if c<0x100 else f'<{c}>' for c in units2[:20])
        print(f"     text@off+8: {txt2}")

dump('static_CH')
dump('static_US')
dump('voice_script_CH')
