# -*- coding: utf-8 -*-
"""导出 fnt_chinese 的 vf3 / 纹理 / peg 描述，并 dump peg 头"""
import sys, os, struct, hashlib
sys.path.insert(0, r'F:\sr2-cn')
from _vpp import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
OUT = r'F:\sr2-cn\_fontdump'
os.makedirs(OUT, exist_ok=True)

def grab(vppname, entname, outname, idx=0):
    v = Vpp(os.path.join(GAME, vppname))
    n = 0
    for e in v.entries():
        if e['name'].lower() == entname.lower():
            if n == idx:
                body = v.read(e)
                open(os.path.join(OUT, outname), 'wb').write(body)
                print("%s :: %s -> %s (%d bytes)" % (vppname, entname, outname, len(body)))
                return body
            n += 1
    print("MISS %s %s" % (vppname, entname))
    return None

vf3 = grab('common.vpp_pc', 'fnt_chinese', 'fnt_chinese.vf3_pc')
tex = grab('patch.vpp_pc', 'fnt_chinese', 'fnt_chinese.tex', 0)
peg = grab('pegs.vpp_pc', 'fnt_chinese', 'fnt_chinese.peg')

print("\n=== peg dump ===")
if peg:
    for i in range(0, len(peg), 16):
        chunk = peg[i:i+16]
        print("  %04X  %s  |%s|" % (i, ' '.join('%02X' % b for b in chunk),
              ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)))

print("\n=== vf3 header (first 256 bytes) ===")
if vf3:
    for i in range(0, 256, 16):
        chunk = vf3[i:i+16]
        print("  %04X  %s  |%s|" % (i, ' '.join('%02X' % b for b in chunk),
              ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)))
    print("\n  u32[0..15]:", struct.unpack_from('<16I', vf3, 0))
