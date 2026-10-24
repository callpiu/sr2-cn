# -*- coding: utf-8 -*-
# 验证最小化修改: 只有 4 个 pointer 变化，其余完全不变
import struct, os, sys
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
orig = Vpp(r"F:/sr2-cn/_backup_B3/patch.vpp_pc.original").read(
    Vpp(r"F:/sr2-cn/_backup_B3/patch.vpp_pc.original").find("static_CH", "le_strings"))
mod = v.read(v.find("static_CH", "le_strings"))

magic, ver, buckets, count = struct.unpack_from("<I H H I", orig, 0)
ptr_off = 12 + buckets * 8

diffs = 0
for i in range(count):
    p1 = struct.unpack_from("<I", orig, ptr_off + i*4)[0]
    p2 = struct.unpack_from("<I", mod, ptr_off + i*4)[0]
    if p1 != p2:
        h1 = struct.unpack_from("<I", orig, p1)[0] if p1 < len(orig)-4 else None
        h2 = struct.unpack_from("<I", mod, p2)[0] if p2 < len(mod)-4 else None
        print("  pointer[%d] %08x -> %08x  key orig=%08x mod=%08x" % (i, p1, p2, h1, h2))
        diffs += 1

print("pointer array 总差异:", diffs)

# bucket table
bt_diff = 0
for i in range(buckets):
    b1 = orig[12+i*8:12+(i+1)*8]
    b2 = mod[12+i*8:12+(i+1)*8]
    if b1 != b2: bt_diff += 1
print("bucket table 差异:", bt_diff)

# header
hdr_ok = orig[:12] == mod[:12]
print("header 相同:", hdr_ok)
