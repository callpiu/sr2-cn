# -*- coding: utf-8 -*-
"""le_strings 正确解码器 v2
布局: magic(4) ver(4) count(4)
      count * (u32 hash, u32 strtab_off)
      strtab_off -> u32[?] 绝对偏移; 每个偏移 -> UTF-16LE 字符串(NUL 结尾)
      (strtab 的项数由相邻 strtab_off 之差/4 推出)
"""
import struct, os, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'

def read_u16z(raw, off):
    o = off
    out = []
    while o + 1 < len(raw):
        u = struct.unpack_from('<H', raw, o)[0]
        o += 2
        if u == 0:
            break
        out.append(u)
    return out

def load(blob_or_path):
    raw = blob_or_path if isinstance(blob_or_path, (bytes, bytearray)) else open(blob_or_path, 'rb').read()
    magic, ver, count = struct.unpack_from('<III', raw, 0)
    # 收集所有 strtab 偏移，用于推断每表长度
    recs = []
    for i in range(count):
        h, off = struct.unpack_from('<II', raw, 12 + i * 8)
        recs.append((h, off))
    # strtab 边界：所有 off 排序
    offs = sorted(set(o for _, o in recs if 0 < o < len(raw)))
    bounds = {}
    for k, o in enumerate(offs):
        nxt = offs[k + 1] if k + 1 < len(offs) else len(raw)
        bounds[o] = nxt
    result = {}
    for h, o in recs:
        if not (0 < o < len(raw)):
            continue
        nxt = bounds.get(o, len(raw))
        n = (nxt - o) // 4
        arr = []
        for k in range(n):
            sub = struct.unpack_from('<I', raw, o + k * 4)[0]
            if 0 < sub < len(raw):
                arr.append(read_u16z(raw, sub))
        result[h] = arr
    return raw, magic, ver, count, result

for p in [os.path.join(G, 'Mods', 'static_US.le_strings')]:
    raw, magic, ver, count, R = load(p)
    print('===', os.path.basename(p), 'count=', count, 'keys=', len(R))
    for h in list(R)[:3]:
        arr = R[h]
        txt = '|'.join(''.join(chr(u) if 0x20 <= u <= 0x7E else '.' for u in s) for s in arr[:2])
        print('  h=%08X n=%d  %s' % (h, len(arr), txt[:100]))
