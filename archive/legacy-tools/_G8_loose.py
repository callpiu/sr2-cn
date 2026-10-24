# -*- coding: utf-8 -*-
"""★★★ 决定性：在所有【松散 le_strings】里搜索 REC1/REC2 的 hash 与槽位

JUICED 的 loose.txt 会加载 Mods/ 下的松散文件覆盖 VPP。
若字幕来自某个松散文件，则改 VPP 完全无效！
"""
import sys, os, struct, glob
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"

def parse(data):
    if len(data) < 12:
        return None
    magic, ver, buckets, count = struct.unpack_from('<IHHI', data, 0)
    if magic != 0xA84C7F73:
        return None
    ptra = 12 + buckets * 8
    if ptra + count*4 > len(data):
        return None
    offs = struct.unpack_from('<%dI' % count, data, ptra)
    out = []
    for off in set(offs):
        if off + 4 > len(data):
            continue
        i1, i2 = struct.unpack_from('<HH', data, off)
        j = off + 4
        sl = []
        while j + 2 <= len(data):
            s = struct.unpack_from('>H', data, j)[0]
            if s == 0:
                break
            sl.append(s); j += 2
        out.append((i1, i2, off, sl))
    return out

TARGETS = {0x84F287ED: "REC1", 0x10AF1E62: "REC2"}

files = []
for root, dirs, fs in os.walk(G):
    for f in fs:
        if f.lower().endswith(('.le_strings', '.cxt')):
            files.append(os.path.join(root, f))
print("找到 %d 个 le_strings/cxt 文件" % len(files))

# 也检查 patch.vpp_pc / common.vpp_pc 内的
vp = Vpp(os.path.join(G, "patch.vpp_pc"))
for x in vp.entries():
    if x['ext'] == 'le_strings':
        d = vp.read(x)
        r = parse(d)
        if not r:
            continue
        for i1, i2, off, sl in r:
            h = (i1 << 16) | i2
            if h in TARGETS:
                print("  [patch.vpp_pc/%s] %s hash=%08X n=%d slots=%s" % (
                    x['name'], TARGETS[h], h, len(sl), sl[:12]))

for p in files:
    try:
        d = open(p, 'rb').read()
    except Exception:
        continue
    r = parse(d)
    if not r:
        continue
    for i1, i2, off, sl in r:
        h = (i1 << 16) | i2
        if h in TARGETS:
            print("  [%s] %s hash=%08X n=%d slots=%s" % (
                os.path.relpath(p, G), TARGETS[h], h, len(sl), sl[:12]))
        # 也找含 slot 403,1868,1035 的串（不管 hash）
        if len(sl) > 8 and 403 in sl and 1868 in sl:
            print("  [%s] 含 你的 槽位 hash=%08X n=%d" % (
                os.path.relpath(p, G), h, len(sl)))
print("搜索完成")
