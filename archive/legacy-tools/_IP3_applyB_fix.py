# -*- coding: utf-8 -*-
# 方案 B 修正版: pointer array 与 records_blob 顺序一致
import os, sys, re, struct, shutil
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
PK = os.path.join(G, "patch.vpp_pc")

TARGETS = [0x84F287ED, 0x10AF1E62, 0xEC2D9F07, 0xE52F931A]

# 备份
backup = r"F:/sr2-cn/_backup_B2/patch.vpp_pc.before_safeB2"
os.makedirs(os.path.dirname(backup), exist_ok=True)
shutil.copy2(PK, backup)
print("备份:", backup)

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

v = Vpp(PK)
e_ch = v.find("static_CH", "le_strings")
e_us = v.find("static_US", "le_strings")
d_ch = v.read(e_ch)
d_us = v.read(e_us)

magic, ver, buckets, count, recs_ch = ls_parse(d_ch)
_, _, _, _, recs_us = ls_parse(d_us)
us_map = {h: (raw, slots) for h, raw, slots in recs_us}

# 替换
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

# 建立 hash -> idx 映射
idx_map = {h: i for i, (h, raw, slots) in enumerate(new_recs)}

# 按 hash % buckets 分组，生成 pointer array 顺序
groups = [[] for _ in range(buckets)]
for h, raw, slots in new_recs:
    groups[h % buckets].append(h)

ptr_array_hashes = []
bucket_tbl = b''
current_ptr_idx = 0
for bidx in range(buckets):
    g = groups[bidx]
    count_b = len(g)
    offset_b = 12 + buckets * 8 + current_ptr_idx * 4
    bucket_tbl += struct.pack("<II", count_b, offset_b)
    for h in g:
        ptr_array_hashes.append(h)
    current_ptr_idx += count_b

assert len(ptr_array_hashes) == count

# 按 ptr_array_hashes 的顺序打包 records
records_blob = b''
ptr_offsets = {}
for h in ptr_array_hashes:
    idx = idx_map[h]
    raw = new_recs[idx][1]
    ptr_offsets[h] = 12 + buckets * 8 + len(ptr_array_hashes) * 4 + len(records_blob)
    records_blob += raw

ptr_blob = b''
for h in ptr_array_hashes:
    ptr_blob += struct.pack("<I", ptr_offsets[h])

out = struct.pack("<I H H I", magic, ver, buckets, count)
out += bucket_tbl
out += ptr_blob
out += records_blob

print("重建后大小:", len(out), "B (原", len(d_ch), "B)")

# 验证: 对比前 64 字节
match = all(out[i] == d_ch[i] for i in range(min(64, len(out), len(d_ch))))
print("前 64 字节匹配:", match)

# 验证 pointer array 前 10 项
diff = 0
for i in range(10):
    p1 = struct.unpack_from("<I", d_ch, 12 + buckets*8 + i*4)[0]
    p2 = struct.unpack_from("<I", out, 12 + buckets*8 + i*4)[0]
    if p1 != p2: diff += 1
print("pointer array 前 10 项差异:", diff)

# 保存
v.replace_body_appended(e_ch, out, align=0x800)
v.save(PK)

import hashlib
md5 = hashlib.md5(open(PK, "rb").read()).hexdigest()
print("patch.vpp_pc md5:", md5)
print("\n回滚:")
print('  cp "F:/sr2-cn/_backup_B2/patch.vpp_pc.before_safeB2" "' + PK + '"')
print("\n判据: 字幕变为英文且无乱码")
