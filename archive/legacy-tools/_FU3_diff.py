"""FU3: diff the reference patch's charlist / vf3 against ours.
"""
import sys, os, struct, re, hashlib
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
REF = r"F:\sr2-cn\_ref92\黑道圣徒2简体汉化补丁\patch.vpp_pc"

def cl_raw(path):
    v = Vpp(path); e = v.find("charlist_CH", "txt")
    return v.read(e)

a = cl_raw(REF)
b = cl_raw(os.path.join(G, "patch.vpp_pc"))
print("ref  charlist_CH size=%d md5=%s" % (len(a), hashlib.md5(a).hexdigest()[:12]))
print("mine charlist_CH size=%d md5=%s" % (len(b), hashlib.md5(b).hexdigest()[:12]))
print("ref  head:", a[:260])
print("mine head:", b[:260])
print()
for tag, d in (("ref", a), ("mine", b)):
    m = re.search(rb"count=(\d+)", d)
    print("%s count match: %r" % (tag, m.group(0) if m else None))
    # count decimal numbers
    body = d[m.end():] if m else d
    nums = re.findall(rb"\d+", body)
    print("   numbers after count= : %d" % len(nums))

# ---- vf3 diff ----
def vf3(path):
    v = Vpp(path); e = v.find("fnt_chinese", "vf3_pc")
    return v.read(e)

ra = vf3(REF)
rb = vf3(os.path.join(G, "patch.vpp_pc"))
print()
print("vf3 ref  md5=%s  size=%d" % (hashlib.md5(ra).hexdigest()[:12], len(ra)))
print("vf3 mine md5=%s  size=%d" % (hashlib.md5(rb).hexdigest()[:12], len(rb)))
n = struct.unpack_from("<I", ra, 8)[0]
print("N(ref)=%d N(mine)=%d" % (n, struct.unpack_from("<I", rb, 8)[0]))
print("header equal:", ra[:0xBC] == rb[:0xBC])
if ra[:0xBC] != rb[:0xBC]:
    for i in range(0xBC):
        if ra[i] != rb[i]:
            print("   hdr diff @0x%02X ref=%02X mine=%02X" % (i, ra[i], rb[i]))

base = 0xBC
rec_diff = [k for k in range(n) if ra[base+k*16:base+k*16+16] != rb[base+k*16:base+k*16+16]]
print("record diffs:", len(rec_diff), rec_diff[:20])
for k in rec_diff[:10]:
    print("   rec %-5d ref=%s mine=%s" % (
        k, struct.unpack_from("<IIII", ra, base+k*16), struct.unpack_from("<IIII", rb, base+k*16)))

uo = base + n*16
Ua = struct.unpack_from("<%dI" % n, ra, uo)
Ub = struct.unpack_from("<%dI" % n, rb, uo)
Va = struct.unpack_from("<%dI" % n, ra, uo + n*4)
Vb = struct.unpack_from("<%dI" % n, rb, uo + n*4)
ud = [k for k in range(n) if Ua[k] != Ub[k]]
vd = [k for k in range(n) if Va[k] != Vb[k]]
print("U diffs:", len(ud), ud[:20])
print("V diffs:", len(vd), vd[:20])
for k in ud[:10]:
    print("   U[%d] ref=%d mine=%d   V ref=%d mine=%d" % (k, Ua[k], Ub[k], Va[k], Vb[k]))
print("U ref  [0:8]:", Ua[:8], " V:", Va[:8])
print("U mine [0:8]:", Ub[:8], " V:", Vb[:8])
