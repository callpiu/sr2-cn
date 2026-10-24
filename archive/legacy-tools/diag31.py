# -*- coding: utf-8 -*-
# inspect music3.vpp_pc hash hits context + container entries
import sys, struct
sys.path.insert(0, 'F:/sr2-cn')

M3 = r'G:\SteamLibrary\steamapps\common\Saints Row 2\music3.vpp_pc'
import os
print('music3 size:', os.path.getsize(M3))
f = open(M3, 'rb')

OFFS = [0x2858869, 0x418ED17, 0x2BD3D355, 0x3D41EC23]
for off in OFFS:
    f.seek(max(0, off - 48))
    ctx = f.read(160)
    print('--- around 0x%X ---' % off)
    print(ctx.hex())
    # printable ascii view
    print(''.join(chr(c) if 32 <= c < 127 else '.' for c in ctx))

# check header / try parse as vpp
f.seek(0)
head = f.read(0x800)
print('magic bytes:', head[:16].hex())
try:
    from sr2lib import Vpp
    vpp = Vpp(M3)
    ents = list(vpp.entries())
    print('entries:', len(ents))
    from collections import Counter
    exts = Counter(e['ext'] for e in ents)
    print('ext census:', dict(exts))
    for e in ents:
        if 'le_strings' in e['ext'] or 'static' in e['name'].lower() or 'text' in e['name'].lower() or 'string' in e['name'].lower():
            print('  INTERESTING:', e['name'], e['ext'], e['size'], 'body=', e.get('body'))
except Exception as ex:
    print('Vpp parse failed:', ex)
