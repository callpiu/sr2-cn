"""FY1: dump the fnt_chinese.vf3_pc structure and the U/V tables for the
indices involved in the two broken subtitles.
"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def load(path, name, ext):
    v = Vpp(path); e = v.find(name, ext) if ext else v.find(name)
    return v.read(e)

for tag, path, name, ext in [
    ("installed", os.path.join(G, "patch.vpp_pc"), "fnt_chinese", "vf3_pc"),
    ("official ", r"F:\sr2-cn\vpp_backup\patch.vpp_pc.orig", "fnt_chinese", "vf3_pc"),
]:
    b = load(path, name, ext)
    n = struct.unpack_from("<I", b, 8)[0]
    print("=" * 70)
    print("%s  len=%d  magic=%r  count@8=%d" % (tag, len(b), b[:4], n))
    print("  header hex:", b[:0xD0].hex())
    # 0xBC header + N*16 records + N*4 U + N*4 V  => total = 0xBC + N*24
    for base in (0xBC, 0xD0):
        tot = base + n * 24
        print("  guess base=0x%02X -> expect %d bytes (actual %d) %s" % (
            base, tot, len(b), "MATCH" if tot == len(b) else "no"))
    # find the U/V tables
    for base in (0xBC, 0xD0):
        off_u = base + n * 16
        if off_u + n * 8 <= len(b):
            U = struct.unpack_from("<%dI" % n, b, off_u)
            V = struct.unpack_from("<%dI" % n, b, off_u + n * 4)
            print("  base=0x%02X U[0:6]=%s V[0:6]=%s" % (base, U[:6], V[:6]))
    print()

# detailed U/V for installed
b = load(os.path.join(G, "patch.vpp_pc"), "fnt_chinese", "vf3_pc")
n = struct.unpack_from("<I", b, 8)[0]
base = 0xBC if 0xBC + n * 24 == len(b) else 0xD0
off_u = base + n * 16
U = struct.unpack_from("<%dI" % n, b, off_u)
V = struct.unpack_from("<%dI" % n, b, off_u + n * 4)
print("installed base=0x%02X n=%d" % (base, n))
IDX = [371, 336, 1836, 1784, 1035, 410, 422, 967, 332, 362, 2667, 2656, 2296, 2268, 391, 354, 1190, 2342]
print("idx     U       V       colU=(U-1)/31  rowV=(V-1)/31   cell=row*65+col")
for i in IDX:
    cu = (U[i] - 1) / 31.0
    rv = (V[i] - 1) / 31.0
    cell = int(round(rv)) * 65 + int(round(cu))
    print("%-6d  %-7d %-7d %-13.2f %-14.2f %d" % (i, U[i], V[i], cu, rv, cell))
