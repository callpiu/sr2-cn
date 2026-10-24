# -*- coding: utf-8 -*-
# 方案 B 修正版 v2: 最小化修改 —— 只替换4条记录内容，把它们移到文件末尾，只改对应4个 pointer
import os, sys, re, struct, shutil
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp

G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
PK = os.path.join(G, "patch.vpp_pc")
TARGETS = set([0x84F287ED, 0x10AF1E62, 0xEC2D9F07, 0xE52F931A])

backup = r"F:/sr2-cn/_backup_B3/patch.vpp_pc.before_safeB3"
os.makedirs(os.path.dirname(backup), exist_ok=True)
shutil.copy2(PK, backup)
print("备份:", backup)

v = Vpp(PK)
e_ch = v.find("static_CH", "le_strings")
e_us = v.find("static_US", "le_strings")
d_ch = bytearray(v.read(e_ch))
d_us = v.read(e_us)

magic, ver, buckets, count = struct.unpack_from("<I H H I", d_ch, 0)
ptr_off = 12 + buckets * 8

# 解析 pointer array
ptrs = [struct.unpack_from("<I", d_ch, ptr_off + i*4)[0] for i in range(count)]

# 解析记录
recs = {}  # hash -> (pointer_index, raw_bytes)
for i, p in enumerate(ptrs):
    id1, id2 = struct.unpack_from("<HH", d_ch, p)
    h = (id1 << 16) | id2
    q = p + 4
    while q + 2 <= len(d_ch):
        w = struct.unpack_from(">H", d_ch, q)[0]
        if w == 0: break
        q += 2
    raw = bytes(d_ch[p:q+2])
    recs[h] = (i, raw)

# 解析 US 记录
us_recs = {}
_, _, bu, cu = struct.unpack_from("<I H H I", d_us, 0)
pu_off = 12 + bu * 8
us_ptrs = [struct.unpack_from("<I", d_us, pu_off + i*4)[0] for i in range(cu)]
for i, p in enumerate(us_ptrs):
    id1, id2 = struct.unpack_from("<HH", d_us, p)
    h = (id1 << 16) | id2
    q = p + 4
    while q + 2 <= len(d_us):
        w = struct.unpack_from(">H", d_us, q)[0]
        if w == 0: break
        q += 2
    raw = d_us[p:q+2]
    us_recs[h] = raw

# 最小化修改: 对4条目标记录，用 US 内容替换，并追加到文件末尾
new_tail = b''
tail_offset = len(d_ch)
modified = 0
for h in TARGETS:
    if h not in recs:
        print("!! %08X not in CH" % h); continue
    if h not in us_recs:
        print("!! %08X not in US" % h); continue
    idx, old_raw = recs[h]
    new_raw = us_recs[h]
    # 写入新位置
    new_ptr = tail_offset + len(new_tail)
    new_tail += new_raw
    # 修改 pointer array
    struct.pack_into("<I", d_ch, ptr_off + idx * 4, new_ptr)
    print("  %08X: ptr %08x -> %08x  len %d -> %d" % (h, ptrs[idx], new_ptr, len(old_raw), len(new_raw)))
    modified += 1

# 追加新记录到末尾
d_ch += new_tail

print("修改记录数:", modified)
print("新大小:", len(d_ch), "B (原", len(v.read(e_ch)), "B)")

# 保存
v.replace_body_appended(e_ch, bytes(d_ch), align=0x800)
v.save(PK)

import hashlib
md5 = hashlib.md5(open(PK, "rb").read()).hexdigest()
print("patch.vpp_pc md5:", md5)
print("\n回滚:")
print('  cp "F:/sr2-cn/_backup_B3/patch.vpp_pc.before_safeB3" "' + PK + '"')
print("\n判据: 字幕变为英文且无乱码")
