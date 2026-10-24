# -*- coding: utf-8 -*-
import struct
G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/DLC/Text/'
raw = open(G + 'dlc_us.le_strings', 'rb').read()

def parse_from(T):
    o = T; ents = []
    while o + 4 <= len(raw):
        h = struct.unpack_from('>I', raw, o)[0]; o += 4
        cps = []
        while o + 2 <= len(raw):
            u = struct.unpack_from('>H', raw, o)[0]; o += 2
            if u == 0: break
            cps.append(u)
        ents.append((o - 4, h, ''.join(chr(c) for c in cps)))
    return ents

for T in (0x1330, 0x1364):
    ents = parse_from(T)
    byT = {e[0] + 4: e for e in ents}
    arr = [struct.unpack_from('<I', raw, 0x408 + i * 4)[0] for i in range(982)]
    miss = [(i, hex(a)) for i, a in enumerate(arr) if a not in byT]
    print('T=0x%X 条目%d  数组(0x408起982条)未命中 %d 个: %s' % (T, len(ents), len(miss), miss[:6]))

print()
print('--- 0x12E0..0x13A0 ---')
for i in range(0x12E0, 0x13A0, 16):
    row = raw[i:i + 16]
    print('%08X  %s |%s|' % (i, ' '.join('%02x' % c for c in row).ljust(47),
          ''.join(chr(c) if 32 <= c < 127 else '.' for c in row)))

# 0x1330 起的 4 条“记录”长什么样
ents = parse_from(0x1330)
print()
for e in ents[:8]:
    print('0x%X hash=0x%08X text=%r' % (e[0], e[1], e[2][:60]))
