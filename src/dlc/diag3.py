# -*- coding: utf-8 -*-
import struct
G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/DLC/Text/'
raw = open(G + 'dlc_us.le_strings', 'rb').read()
N = len(raw)

def hexd(b, n, off):
    out = []
    for i in range(0, min(n, len(b) - off), 16):
        row = b[off + i: off + i + 16]
        out.append('%08X  %s |%s|' % (off + i, ' '.join('%02x' % c for c in row).ljust(47),
                   ''.join(chr(c) if 32 <= c < 127 else '.' for c in row)))
    return '\n'.join(out)

# 1) 128 对表
pairs = [struct.unpack_from('<II', raw, 8 + i * 8) for i in range(128)]
offs = [p[0] for p in pairs]
lens = [p[1] for p in pairs]
print('offsets 单调递增?', all(offs[i] < offs[i+1] for i in range(127)))
print('offsets 范围', offs[0], offs[-1])
print('lens   范围', min(lens), max(lens))
print('lens 前20', lens[:20])
print('表之后 8 字节 @0x408:', raw[0x408:0x418].hex())

# 2) 找 UTF-16BE 可打印 ASCII 长串
runs = []
i = 0
while i + 2 <= N:
    if raw[i] == 0 and 32 <= raw[i+1] < 127:
        j = i
        cnt = 0
        while j + 2 <= N and raw[j] == 0 and 32 <= raw[j+1] < 127:
            cnt += 1; j += 2
        if cnt >= 8:
            runs.append((i, cnt))
        i = j
    else:
        i += 1
print('长 ASCII(BE) 串数量', len(runs), '首个', runs[0] if runs else None)
print('前 10 个:', runs[:10])

# 3) 首个文本串附近
if runs:
    s = runs[0][0]
    print('--- 文本首串 0x%X 前后 ---' % s)
    print(hexd(raw, 96, max(0, s - 32)))
    # 该处往前 4 字节当 hash
    print('前4字节 BE=0x%08X LE=0x%08X' % (
        struct.unpack_from('>I', raw, s - 4)[0], struct.unpack_from('<I', raw, s - 4)[0]))

# 4) 0x40C 起的 u32 数组
arr = [struct.unpack_from('<I', raw, 0x40C + i * 4)[0] for i in range(20)]
print('0x40C 起 u32:', ['0x%X' % a for a in arr])
print('是否递增:', all(arr[i] < arr[i+1] for i in range(19)))
