# -*- coding: utf-8 -*-
"""DLC le_strings 结构逆向：搞清楚开头的索引表"""
import struct

G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/DLC/Text/'

def hexd(b, n=64, off=0):
    out = []
    for i in range(0, min(n, len(b) - off), 16):
        row = b[off + i: off + i + 16]
        out.append('%08X  %s  |%s|' % (
            off + i,
            ' '.join('%02x' % c for c in row).ljust(47),
            ''.join(chr(c) if 32 <= c < 127 else '.' for c in row)))
    return '\n'.join(out)

raw = open(G + 'dlc_us.le_strings', 'rb').read()
print('size', len(raw))
print('--- 0x380..0x460 ---')
print(hexd(raw, 0xE0, 0x380))

# 头部
magic, unk = struct.unpack_from('<II', raw, 0)
print('magic=0x%08X unk=0x%08X' % (magic, unk))

# 从 8 开始读 (offset,len) 对，直到 offset 越界或不再递增
pairs = []
o = 8
while o + 8 <= len(raw):
    off, ln = struct.unpack_from('<II', raw, o)
    if off > len(raw) or (pairs and off <= pairs[-1][0] and ln < 0x10000):
        pass
    pairs.append((off, ln))
    o += 8
    if off > 0x2000:  # 表显然很小，先截断看
        break
print('前 12 对:', pairs[:12])
print('第 12..24 对:', pairs[12:24])

# 找到第一个 offset 指向的位置，验证是不是 (hash + UTF-16BE + 0x0000)
first = pairs[0][0]
print('--- 文本区起点 0x%X ---' % first)
print(hexd(raw, 0x60, first))
h0 = struct.unpack_from('>I', raw, first)[0]
print('该处 u32(BE)=0x%08X', hex(h0))
