import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load_charlist(path, name="charlist_CH"):
    v = Vpp(path); e = v.find(name, "txt")
    t = v.read(e).decode("utf-8", "replace").replace("\r", "").split("\n")
    return [int(s) for s in t if s.strip().isdigit()]

M = load_charlist(os.path.join(G, "patch.vpp_pc"))
O = load_charlist(r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig")

def show(T, a, b):
    return "".join(chr(c) if 32 <= c < 0x110000 else "?" for c in T[a:b])

print("M len", len(M), " O len", len(O))
print("M[0:96]   =", repr(show(M, 0, 96)))
print("M[96:128] =", repr(show(M, 96, 128)))
print("O[0:96]   =", repr(show(O, 0, 96)))
print("O[96:128] =", repr(show(O, 96, 128)))
print()
print("M 前 16 项码点:", [hex(c) for c in M[:16]])
print("O 前 16 项码点:", [hex(c) for c in O[:16]])
print()

vp = Vpp(os.path.join(G, "patch.vpp_pc"))
b = vp.read(vp.find("static_CH", "le_strings"))
n = struct.unpack_from("<I", b, 8)[0]
print("static_CH n =", n, " size =", len(b))
print("header hex:", b[:24].hex())
print()
print("directory first 10 (a,b):")
for i in range(10):
    a = struct.unpack_from("<I", b, 16 + i*8)[0]
    c = struct.unpack_from("<I", b, 20 + i*8)[0]
    print("   [%2d] a=%-8d (0x%08X)  b=%-8d (0x%08X)" % (i, a, a, c, c))
print()
start = 16 + n*8
print("text area start =", start, " first 64 bytes:")
for o in range(start, start + 64, 16):
    row = b[o:o+16]
    print("   %06x  %s  |%s|" % (o, " ".join("%02x" % x for x in row),
          "".join(chr(x) if 32 <= x < 127 else "." for x in row)))
