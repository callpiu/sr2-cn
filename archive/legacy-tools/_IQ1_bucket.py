# -*- coding: utf-8 -*-
# 解析 bucket table 格式
import struct, os, sys
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))

def parse(data):
    magic, ver, buckets, count = struct.unpack_from("<I H H I", data, 0)
    off = 12
    bt = data[off:off+buckets*8]
    off += buckets*8
    ptrs = [struct.unpack_from("<I", data, off+i*4)[0] for i in range(count)]
    recs = []
    for p in ptrs:
        id1, id2 = struct.unpack_from("<HH", data, p)
        q = p+4; slots = []
        while q+2 <= len(data):
            w = struct.unpack_from(">H", data, q)[0]
            if w == 0: break
            slots.append(w); q += 2
        recs.append(((id1<<16)|id2, slots))
    return magic, ver, buckets, count, bt, ptrs, recs

for nm in ["static_CH", "static_US"]:
    e = v.find(nm, "le_strings")
    d = v.read(e)
    magic, ver, buckets, count, bt, ptrs, recs = parse(d)
    print("\n=== %s === buckets=%d count=%d" % (nm, buckets, count))
    # 打印前 10 个非空 bucket
    non_empty = 0
    for i in range(min(buckets, 20)):
        b = bt[i*8:(i+1)*8]
        a, b0, c, d0 = struct.unpack_from("<HHHH", b, 0)
        x, y = struct.unpack_from("<II", b, 0)
        if x != 0 or y != 0:
            print("  bucket[%4d]  u32=%08x %08x  u16=%04x %04x %04x %04x" % (i, x, y, a, b0, c, d0))
            non_empty += 1
    print("  非空 bucket (前20) =", non_empty)
    # hash 分布: 看 key % buckets 落在哪些 bucket
    for h, s in recs[:5]:
        print("  rec %08x  slots=%d  hash%%buckets=%d" % (h, len(s), h % buckets))
