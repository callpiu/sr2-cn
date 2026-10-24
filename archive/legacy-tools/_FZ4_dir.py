"""FZ4: understand the .le_strings directory so we can rebuild it safely.
"""
import sys, os, struct, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
b = v.read(v.find("static_CH", "le_strings"))
n = struct.unpack_from("<I", b, 8)[0]
print("size=%d  n=%d  dir=%d..%d  codes_start=%d" % (len(b), n, 16, 16+n*8, 16+n*8))
print("header hex:", b[:16].hex())
print("hdr u32:", struct.unpack_from("<4I", b, 0))

print()
print("dir[0:6] :", [struct.unpack_from("<2I", b, 16+i*8) for i in range(6)])
print("dir[last4]:", [struct.unpack_from("<2I", b, 16+i*8) for i in range(n-4, n)])

# pieces
codes_off = 16 + n*8
nc = (len(b) - codes_off)//2
codes = list(struct.unpack_from(">%dH" % nc, b, codes_off))
pieces = []
cur = 0
for i, c in enumerate(codes):
    if c == 0:
        pieces.append((cur, i)); cur = i+1
print("pieces found:", len(pieces))

print()
print("first 6 dir entries vs piece start/id:")
for i in range(6):
    a, d = struct.unpack_from("<2I", b, 16+i*8)
    st, en = pieces[i] if i < len(pieces) else (None, None)
    pid = (codes[st] << 16) | codes[st+1] if st is not None else None
    print("   dir[%d] = (0x%08X, 0x%08X)   piece[%d] st=%s id=%s" % (i, a, d, i, st, hex(pid) if pid else None))

print()
print("check: dir[i][0] == piece start? dir[i][1] == id?")
okA = okB = 0
for i in range(min(50, len(pieces))):
    a, d = struct.unpack_from("<2I", b, 16+i*8)
    st, en = pieces[i]
    pid = (codes[st] << 16) | codes[st+1]
    if a == st: okA += 1
    if d == pid: okB += 1
print("   dir[.][0]==start: %d/50   dir[.][1]==id: %d/50" % (okA, okB))

print()
print("piece #3461 dir entry:")
a, d = struct.unpack_from("<2I", b, 16+3461*8)
st, en = pieces[3461]
pid = (codes[st] << 16) | codes[st+1]
print("   dir=(0x%08X, 0x%08X)  piece st=%d en=%d id=0x%08X" % (a, d, st, en, pid))
