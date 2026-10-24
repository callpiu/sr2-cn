"""diag15: inspect VFNT per-glyph records (spacing,byteWidth,offset,kerning)
for patch vs common fnt_chinese at the suspect slots. The 'offset' field may be
the real glyph-cell position. Compare against the in-game screen charlist idx."""
import sys, struct
sys.path.insert(0, r'F:\sr2-cn')
from sr2lib import Vpp, parse_vfnt

PATCH = r'G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc'
COMMON = r'G:\SteamLibrary\steamapps\common\Saints Row 2\common.vpp_pc'
patch = Vpp(PATCH); common = Vpp(COMMON)

pb = patch.read(patch.find('fnt_chinese', 'vf3_pc'))
cb = common.read(common.find('fnt_chinese', 'vf3_pc'))

hp, recs_p, _ = parse_vfnt(pb)
hc, recs_c, _ = parse_vfnt(cb)
print('patch recs', len(recs_p), 'common recs', len(recs_c))
print('patch header first 16 bytes:', hp[:16].hex())

# stats on offset field
import collections
off_p = collections.Counter(r[2] for r in recs_p)
off_c = collections.Counter(r[2] for r in recs_c)
print('patch offset distinct values (top):', off_p.most_common(5))
print('common offset distinct values (top):', off_c.most_common(5))
print('patch offset min/max:', min(r[2] for r in recs_p), max(r[2] for r in recs_p))
print('common offset min/max:', min(r[2] for r in recs_c), max(r[2] for r in recs_c))

slots = {371:336, 1836:1784, 1035:410, 422:967, 332:362,
         2667:2656, 2296:2268, 391:354, 1190:2342}
print('\nidx   patch(sp,bw,off,kern)          common(sp,bw,off,kern)        screen')
for idx, sv in slots.items():
    rp = recs_p[idx]
    rc = recs_c[idx]
    print('%5d  %-30s %-30s %d' % (idx, str(rp), str(rc), sv))

# Does offset (field 2) or spacing (field 0) or byteWidth (field1) match screen idx?
for field in range(4):
    name = ['spacing','byteWidth','offset','kerning'][field]
    okp = sum(1 for idx,sv in slots.items() if recs_p[idx][field] == sv)
    okc = sum(1 for idx,sv in slots.items() if recs_c[idx][field] == sv)
    print('field %s matches screen idx: patch %d/%d common %d/%d' % (name, okp, len(slots), okc, len(slots)))

# dump raw tail of patch vf3 to see the U/V arrays content
print('\n--- patch tail @0xAF6C (u16 x16) ---')
print(list(struct.unpack_from('<16H', pb, 0xAF6C)))
print('--- patch tail @0xDB18 (u16 x16) ---')
print(list(struct.unpack_from('<16H', pb, 0xDB18)))
print('--- common @0xAF6C (u16 x16) ---')
print(list(struct.unpack_from('<16H', cb, 0xAF6C)))
print('--- common @0xDB18 (u16 x16) ---')
print(list(struct.unpack_from('<16H', cb, 0xDB18)))
