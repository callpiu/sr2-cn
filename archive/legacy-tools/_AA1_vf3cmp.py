# -*- coding: utf-8 -*-
import sys, struct, io, re, hashlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from _vpp import Vpp

def parse_plain(d):
    body = d.split(b'//ENDOFFILE')[0]
    return [int(x) for x in re.findall(rb'\d+', body)]

CASES = {
    'AUTHOR': r"F:\sr2-cn\_patchsrc\patch.vpp_pc",
    'GAME':   r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc",
}
SLOTS = [403, 1868, 1067, 454, 364, 2699, 2328, 423, 1222]
for tag, p in CASES.items():
    v = Vpp(p)
    vf = v.read(v.find("fnt_chinese", "vf3_pc"))
    N = struct.unpack_from('<I', vf, 8)[0]
    U = struct.unpack_from('<%dI' % N, vf, 0xBC + N*16)
    V = struct.unpack_from('<%dI' % N, vf, 0xBC + N*16 + N*4)
    print("=== %s  vf3 md5=%s N=%d ===" % (tag, hashlib.md5(vf).hexdigest()[:12], N))
    for s in SLOTS:
        print("   slot %4d -> UV(%4d,%4d)" % (s, U[s], V[s]))
    # which index holds the 任 glyph UV (342,156)?
    for i in range(N):
        if (U[i], V[i]) == (342, 156):
            print("   glyph 任(342,156) is at vf3 index", i)
            break
    print("   U[336]=%d V[336]=%d  U[371]=%d V[371]=%d" % (U[336], V[336], U[371], V[371]))
