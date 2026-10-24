# -*- coding: utf-8 -*-
# 对比重建的 static_CH 与原文件，找出导致崩溃的差异
import os, sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
orig = v.read(v.find("static_CH", "le_strings"))

TARGETS = [0x84F287ED, 0x10AF1E62, 0xEC2D9F07, 0xE52F931A]

def ls_parse(data):
    magic, ver, buckets, count = struct.unpack_from("<I H H I", data, 0)
    off = 12 + buckets * 8
    ptrs = [struct.unpack_from("<I", data, off + i*4)[0] for i in range(count)]
    recs = []
    for p in ptrs:
        id1, id2 = struct.unpack_from("<HH", data, p)
        q = p + 4; slots = []
        while q + 2 <= len(data):
            w = struct.unpack_from(">H", data, q)[0]
            if w == 0: break
            slots.append(w); q += 2
        raw = data[p:q+2]
        recs.append(((id1 << 16) | id2, raw, slots))
    return magic, ver, buckets, count, recs

magic, ver, buckets, count, recs_ch = ls_parse(orig)
recs_us = ls_parse(v.read(v.find("static_US", "le_strings")))[4]
us_map = {h: (raw, slots) for h, raw, slots in recs_us}

# 重建
new_recs = []
for h, raw, slots in recs_ch:
    if h in TARGETS and h in us_map:
        us_raw, us_slots = us_map[h]
        new_raw = struct.pack("<HH", h & 0xFFFF, (h >> 16) & 0xFFFF)
        new_raw += b''.join(struct.pack(">H", w) for w in us_slots)
        new_raw += b'\x00\x00'
        new_recs.append((h, new_raw, us_slots))
    else:
        new_recs.append((h, raw, slots))

groups = [[] for _ in range(buckets)]
for idx, (h, raw, slots) in enumerate(new_recs):
    groups[h % buckets].append(idx)

ptr_array = []
bucket_tbl = b''
current_ptr_idx = 0
for bidx in range(buckets):
    g = groups[bidx]
    count_b = len(g)
    offset_b = 12 + buckets * 8 + current_ptr_idx * 4
    bucket_tbl += struct.pack("<II", count_b, offset_b)
    for idx in g:
        ptr_array.append(idx)
    current_ptr_idx += count_b

records_blob = b''
ptr_offsets = {}
for idx, (h, raw, slots) in enumerate(new_recs):
    ptr_offsets[idx] = 12 + buckets * 8 + len(ptr_array) * 4 + len(records_blob)
    records_blob += raw

ptr_blob = b''
for idx in ptr_array:
    ptr_blob += struct.pack("<I", ptr_offsets[idx])

rebuilt = struct.pack("<I H H I", magic, ver, buckets, count)
rebuilt += bucket_tbl
rebuilt += ptr_blob
rebuilt += records_blob

print("orig =", len(orig), "rebuilt =", len(rebuilt))

# 逐字节对比
first_diff = None
for i in range(min(len(orig), len(rebuilt))):
    if orig[i] != rebuilt[i]:
        first_diff = i
        break
if first_diff is None:
    if len(orig) != len(rebuilt):
        print("无差异到 min 长度，但总长度不同")
    else:
        print("完全无差异！")
else:
    print("首个差异 @offset", first_diff)
    # dump 前后 64 字节
    s = max(0, first_diff - 32)
    e = min(len(orig), first_diff + 32)
    print("orig:", " ".join("%02X" % orig[j] for j in range(s, e)))
    print("rebl:", " ".join("%02X" % rebuilt[j] for j in range(s, e)))
    # 标注差异位
    mark = ""
    for j in range(s, e):
        if j < len(orig) and j < len(rebuilt) and orig[j] != rebuilt[j]:
            mark += "^^ "
        else:
            mark += "   "
    print("     ", mark)

# 更深层检查: pointer array 内容
off_ptr = 12 + buckets * 8
print("\npointer array 对比 (前 20 项):")
for i in range(20):
    p1 = struct.unpack_from("<I", orig, off_ptr + i*4)[0]
    p2 = struct.unpack_from("<I", rebuilt, off_ptr + i*4)[0]
    print("  [%5d] orig=%08x rebuilt=%08x %s" % (i, p1, p2, "OK" if p1==p2 else "DIFF"))

# 随机抽查几个 pointer 指向的记录
print("\nrandom pointer check:")
import random
for i in random.sample(range(count), 10):
    p1 = struct.unpack_from("<I", orig, off_ptr + i*4)[0]
    p2 = struct.unpack_from("<I", rebuilt, off_ptr + i*4)[0]
    # 读记录 key
    k1 = struct.unpack_from("<I", orig, p1)[0] if p1 < len(orig)-4 else None
    k2 = struct.unpack_from("<I", rebuilt, p2)[0] if p2 < len(rebuilt)-4 else None
    print("  [%5d] orig->%08x key=%08x | rebl->%08x key=%08x %s" % (i, p1, k1, p2, k2, "OK" if k1==k2 else "DIFF"))
