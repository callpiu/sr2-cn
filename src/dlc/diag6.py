# -*- coding: utf-8 -*-
import struct
from collections import Counter
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
offs = sorted(e[0] for e in ents)
arr = [struct.unpack_from('<I', raw, 0x408 + i * 4)[0] for i in range(982)]

# 找常数基：arr[i] + C == 条目偏移
c = Counter()
for R in offs:
    for a in arr:
        c[R - a] += 1
print('数组常数基 top8:', [(hex(k) if k >= 0 else k, v) for k, v in c.most_common(8)])

# 桶表 pair=(off,len)：找 off 与「字符数==len 的条目」的常数关系
bk = [struct.unpack_from('<II', raw, 0x08 + i * 8) for i in range(128)]
c2 = Counter()
for off, ln in bk:
    for e in ents:
        if e[3] == ln:
            c2[e[0] - off] += 1
print('桶表常数基 top8:', [(hex(k), v) for k, v in c2.most_common(8)])

# 桶表第二字段是否就是字符数
lens_ok = sum(1 for off, ln in bk if any(e[3] == ln for e in ents))
print('桶表 len 能在条目中找到:', lens_ok, '/128')
# 桶表第一字段是否单调、范围
bo = [p[0] for p in bk]
print('桶表 offset 范围', hex(bo[0]), hex(bo[-1]), '单调?', all(bo[i] < bo[i+1] for i in range(127)))
# 条目大小分布
sizes = [offs[i+1] - offs[i] for i in range(len(offs) - 1)]
print('条目间距 min/max/平均', min(sizes), max(sizes), sum(sizes)//len(sizes))
