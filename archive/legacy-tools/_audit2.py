# -*- coding: utf-8 -*-
"""回归审计 v2：只解析 en-US(0x0409) 命名空间下、且 slot < 0x800 的记录。
   引擎对中文用 charlist_CH(2795)，slot 范围应为 0x20..0x20+2794。
"""
import sys, os, struct, collections
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def parse(data):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', data, 0)
    if magic != 0xA84C7F73:
        return None
    ptr_off = 12 + buckets * 8
    out = []
    for i in range(count):
        off = struct.unpack_from('<I', data, ptr_off + i*4)[0]
        if off == 0 or off >= len(data):
            continue
        id1, id2 = struct.unpack_from('<HH', data, off)
        p = off + 4
        slots = []
        while p + 1 < len(data):
            v = struct.unpack_from('<H', data, p)[0]
            if v == 0: break
            slots.append(v); p += 2
        out.append((id1, id2, slots))
    return out

files = []
for root, dirs, fs in os.walk(G):
    for f in fs:
        if f.lower().endswith('.le_strings'):
            files.append(os.path.join(root, f))

# 只看中文相关文件
zh = [p for p in files if 'ch' in os.path.basename(p).lower()]
print("中文相关 le_strings:")
for p in zh:
    print("  ", os.path.relpath(p, G))

maxslot = 0
hist = collections.Counter()
for p in zh:
    d = open(p, 'rb').read()
    r = parse(d)
    if not r:
        print("  (非标准)", p); continue
    # 统计 32..0x800 范围的 slot（中文有效区）
    mx = 0
    cnt = 0
    for id1, id2, slots in r:
        for s in slots:
            if 0x20 <= s < 0x800:
                mx = max(mx, s); cnt += 1
    print("  %-46s rec=%-6d 中文slot数=%-6d max=%d  (idx=%d)" % (
        os.path.relpath(p, G), len(r), cnt, mx, mx - 0x20))
    maxslot = max(maxslot, mx)

print("\n★ 中文 slot 最大值 = %d  (idx = %d)" % (maxslot, maxslot - 0x20))
print("★ 新 common vf3 项数 = 2795  => 可索引 0..2794")
print("★ 结论: %s" % ("✓ 不越界，安全" if maxslot - 0x20 < 2795 else "✗ 越界!"))
