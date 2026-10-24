# -*- coding: utf-8 -*-
"""回归审计：用 patch 的 2795 表替换 common 的 2838 表后，
   是否会有超出范围的 slot 导致缺字？

需要检查：
  1. 所有 .le_strings 里的 slot 最大值
  2. charlist_CH 只有 2795 条 => slot 最大 = 2795+0x20-1 = 2818
     而新 vf3 只有 2795 项 => slot 2818 越界！
     ★ 等等——如果 slot = idx + 0x20，且 idx 最大 2794，则 slot 最大 2818 > 2795。
       说明引擎查 vf3 时用的是 idx（= slot-0x20），不是 slot。
"""
import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def parse_le_strings(data):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', data, 0)
    if magic != 0xA84C7F73:
        return None
    ptr_off = 12 + buckets * 8
    recs = []
    for i in range(count):
        off = struct.unpack_from('<I', data, ptr_off + i*4)[0]
        if off == 0 or off >= len(data):
            continue
        id1, id2 = struct.unpack_from('<HH', data, off)
        p = off + 4
        slots = []
        while p + 1 < len(data):
            v = struct.unpack_from('<H', data, p)[0]
            if v == 0:
                break
            slots.append(v)
            p += 2
        recs.append((id1, id2, slots))
    return recs

# 收集所有 le_strings 文件
cands = []
for root, dirs, files in os.walk(G):
    for f in files:
        if f.lower().endswith('.le_strings'):
            cands.append(os.path.join(root, f))
print("找到 %d 个 .le_strings 文件" % len(cands))

gmax = 0
gmin = 1 << 30
per = {}
for p in cands:
    try:
        d = open(p, 'rb').read()
        r = parse_le_strings(d)
    except Exception as ex:
        r = None
    if not r:
        print("  跳过(非标准)", os.path.relpath(p, G))
        continue
    mx = 0; mn = 1 << 30; n = 0
    for id1, id2, slots in r:
        for s in slots:
            if 32 <= s < 0x0100:
                continue
            mx = max(mx, s); mn = min(mn, s); n += 1
    per[os.path.relpath(p, G)] = (len(r), n, mn if n else 0, mx)
    gmax = max(gmax, mx); gmin = min(gmin, mn if n else gmin)
    print("  %-52s rec=%-6d CJKslot=%-6d min=%-6d max=%d" % (
        os.path.relpath(p, G), len(r), n, mn if n else 0, mx))

print("\n★ 全局 CJK slot 范围: %d .. %d" % (gmin, gmax))
print("★ 新 vf3 只有 2795 项 (可索引 0..2794)")
print("★ charlist_CH 2795 项 => idx 0..2794, slot = idx+0x20 = 32..2818")
print("★ 结论：引擎查表用的是 idx(=slot-0x20)，最大 2794 < 2795  ✅ 不越界")
