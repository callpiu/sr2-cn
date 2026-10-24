# -*- coding: utf-8 -*-
# 方案 B 安全版: 把 static_CH 中 4 条已知乱码记录替换为 static_US 的英文原文
import os, sys, re, struct, shutil
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
PK = os.path.join(G, "patch.vpp_pc")

TARGETS = [0x84F287ED, 0x10AF1E62, 0xEC2D9F07, 0xE52F931A]

# ---------- 备份 ----------
backup = r"F:/sr2-cn/_backup_B/patch.vpp_pc.before_safeB"
os.makedirs(os.path.dirname(backup), exist_ok=True)
shutil.copy2(PK, backup)
print("备份:", backup)

# ---------- le_strings 解析 ----------
def ls_parse(data):
    magic, ver, buckets, count = struct.unpack_from("<I H H I", data, 0)
    off = 12 + buckets * 8
    ptrs = [struct.unpack_from("<I", data, off + i*4)[0] for i in range(count)]
    recs = []  # (hash, original_bytes, slots)
    for p in ptrs:
        id1, id2 = struct.unpack_from("<HH", data, p)
        q = p + 4; slots = []
        while q + 2 <= len(data):
            w = struct.unpack_from(">H", data, q)[0]
            if w == 0: break
            slots.append(w); q += 2
        # 原始记录字节 = 从 p 到 q+2（含 0x0000 终止符）
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

# 建立 US 查找表
us_map = {h: (raw, slots) for h, raw, slots in recs_us}

# 替换目标记录
modified = 0
new_recs = []
for h, raw, slots in recs_ch:
    if h in TARGETS:
        if h not in us_map:
            print("!! %08X 在 US 表中不存在，跳过" % h)
            new_recs.append((h, raw, slots))
            continue
        us_raw, us_slots = us_map[h]
        # 用 US 的 slots 重建记录（保留相同的 key）
        new_raw = struct.pack("<HH", h & 0xFFFF, (h >> 16) & 0xFFFF)
        new_raw += b''.join(struct.pack(">H", w) for w in us_slots)
        new_raw += b'\x00\x00'
        new_recs.append((h, new_raw, us_slots))
        modified += 1
        print("  替换 %08X: CH slots=%d -> US slots=%d" % (h, len(slots), len(us_slots)))
    else:
        new_recs.append((h, raw, slots))

print("修改记录数:", modified)

# ---------- 重建 le_strings ----------
# 1) 按 hash 分组记录索引
groups = [[] for _ in range(buckets)]
for idx, (h, raw, slots) in enumerate(new_recs):
    groups[h % buckets].append(idx)

# 2) 构建 pointer array（按 bucket 顺序）和 bucket table
ptr_array = []      # 每项 = 绝对文件偏移
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

# 3) 按原始顺序（或任意顺序）打包记录，并计算偏移
# 为了最小化风险，保持记录按原 pointer array 顺序（即按 new_recs 顺序）
# 但 pointer array 本身已经按 bucket 分组了
# 这里我们先把所有记录按 new_recs 顺序打包，然后 pointer array 指向它们
records_blob = b''
ptr_offsets = {}  # idx -> absolute offset
for idx, (h, raw, slots) in enumerate(new_recs):
    ptr_offsets[idx] = 12 + buckets * 8 + len(ptr_array) * 4 + len(records_blob)
    records_blob += raw

# 4) 构建最终 pointer array（用绝对偏移）
ptr_blob = b''
for idx in ptr_array:
    ptr_blob += struct.pack("<I", ptr_offsets[idx])

# 5) 组装
out = struct.pack("<I H H I", magic, ver, buckets, count)
out += bucket_tbl
out += ptr_blob
out += records_blob

print("重建后大小: %d B (原 %d B)" % (len(out), len(d_ch)))

# ---------- 替换并保存 ----------
v.replace_body_appended(e_ch, out, align=0x800)
v.save(PK)

# 校验
import hashlib
md5 = hashlib.md5(open(PK, "rb").read()).hexdigest()
print("patch.vpp_pc md5:", md5)
print("\n回滚命令:")
print('  cp "F:/sr2-cn/_backup_B/patch.vpp_pc.before_safeB" "' + PK + '"')
print("\n判据:")
print("  启动游戏，进入直升机突击任务，看字幕是否变为英文（ readable 无乱码）")
