# -*- coding: utf-8 -*-
import struct
G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/DLC/Text/'
raw = open(G + 'dlc_us.le_strings', 'rb').read()
TEXT0 = 0x1364

ents = []
o = TEXT0
while o + 4 <= len(raw):
    h = struct.unpack_from('>I', raw, o)[0]; o += 4
    cps = []
    while o + 2 <= len(raw):
        u = struct.unpack_from('>H', raw, o)[0]; o += 2
        if u == 0: break
        cps.append(u)
    ents.append((o - 4, h, ''.join(chr(c) for c in cps), len(cps)))
offs = {e[0]: e for e in ents}
print('条目数', len(ents))

for base_name, base in [('abs', 0), ('+0x408', 0x408), ('+0x40C', 0x40C),
                        ('+TEXT0', TEXT0), ('+0x1360', 0x1360)]:
    arr = [struct.unpack_from('<I', raw, 0x408 + i * 4)[0] for i in range(982)]
    hit = sum(1 for a in arr if a + base in offs)
    print('base %-8s 命中 %d/982  min=0x%X max=0x%X' % (base_name, hit, min(arr), max(arr)))

arr = [struct.unpack_from('<I', raw, 0x408 + i * 4)[0] for i in range(982)]
print('arr[0:12]', ['0x%X' % a for a in arr[:12]])
print('arr[-6:]', ['0x%X' % a for a in arr[-6:]])
# 命中项的 hash 序列是否有序（base=0 时）
hs = [offs[a][1] for a in arr if a in offs]
print('base=0 命中', len(hs))
print('这些 hash 单调递减?', all(hs[i] > hs[i+1] for i in range(len(hs)-1)))
print('这些 hash 单调递增?', all(hs[i] < hs[i+1] for i in range(len(hs)-1)))
print('hash 前 8:', ['0x%08X' % h for h in hs[:8]])
# 未命中的值
miss = [a for a in arr if a not in offs][:10]
print('未命中样例', ['0x%X' % m for m in miss])
# 所有条目偏移范围
alloff = sorted(offs)
print('条目偏移 min=0x%X max=0x%X' % (alloff[0], alloff[-1]))
