# -*- coding: utf-8 -*-
"""对比 游戏内 vf3 / 作者原始 vf3 / 官方 vf3"""
import sys, os, struct
sys.path.insert(0, r'F:\sr2-cn')
from _vpp import Vpp

GAME = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
OUT = r'F:\sr2-cn\_fontdump'

def get(vpppath, name, outname, size=None):
    v = Vpp(vpppath)
    for e in v.entries():
        if e['name'].lower() == name:
            if size is not None and e['size'] != size:
                continue
            b = v.read(e)
            p = os.path.join(OUT, outname)
            open(p, 'wb').write(b)
            return b
    return None

game = get(os.path.join(GAME, 'patch.vpp_pc'), 'fnt_chinese', 'vf3_game.bin', 67268)
auth = get(r'F:\sr2-cn\_patchsrc\patch.vpp_pc', 'fnt_chinese', 'vf3_auth.bin', 67268)
offi = get(r'F:\sr2-cn\vpp_backup\patch.vpp_pc.orig', 'fnt_chinese', 'vf3_offi.bin', 68300)
print("game %d auth %d offi %d" % (len(game), len(auth), len(offi)))

def hdr(d, tag):
    print("\n=== %s (%d) ===" % (tag, len(d)))
    print("  magic %r ver %d count %d w %d h %d" % (d[:4], struct.unpack_from('<I', d, 4)[0],
          struct.unpack_from('<I', d, 8)[0], struct.unpack_from('<I', d, 12)[0], struct.unpack_from('<I', d, 16)[0]))
    print("  header bytes 0x00..0xBC identical to game:", d[:0xBC] == game[:0xBC])

hdr(game, 'game')
hdr(auth, 'author')
hdr(offi, 'official')

# 逐字节差异
def diffs(a, b, limit=20):
    n = min(len(a), len(b))
    ds = [i for i in range(n) if a[i] != b[i]]
    print("   差异字节数 %d (比较前 %d 字节)" % (len(ds), n))
    for i in ds[:limit]:
        print("      0x%06X  a=%02X b=%02X" % (i, a[i], b[i]))
    return ds

print("\n--- game vs author ---")
diffs(game, auth)
print("\n--- game vs official ---")
diffs(game, offi)

# 解析两者的 Table A/B
def table(d, N, name):
    A = 0xBC; B = A + N * 16
    P = []; Q = []; W = []; H = []
    for i in range(N):
        w, h, z, f = struct.unpack_from('<4I', d, A + i * 16)
        W.append(w); H.append(h)
        p, q = struct.unpack_from('<2I', d, B + i * 8)
        P.append(p); Q.append(q)
    print("\n%s: N=%d  W[:6]=%s H[:6]=%s" % (name, N, W[:6], H[:6]))
    print("    P[:8]=%s" % P[:8])
    return W, H, P, Q

for d, N, tag in ((game, 2795, 'game'), (auth, 2795, 'author')):
    table(d, N, tag)
