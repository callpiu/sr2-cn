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
byT = {e[0] + 4: e for e in ents}
arr = [struct.unpack_from('<I', raw, 0x408 + i * 4)[0] for i in range(982)]
bk = [struct.unpack_from('<II', raw, 0x08 + i * 8) for i in range(128)]

# 累积计数 → 每桶首个条目在数组中的下标
cum, k = [], 0
for off, ln in bk:
    cum.append(k); k += ln
print('累积和末尾', k)
print('各组首条目文本指针 arr[cum_i] 前 8:', ['0x%X' % arr[c] for c in cum[:8]])
print('桶表 off       前 8:', ['0x%X' % b[0] for b in bk[:8]])
d = Counter(arr[c] - bk[i][0] for i, c in enumerate(cum))
print('arr[cum_i] - bk[i].off 的常数 top5:', [(hex(k), v) for k, v in d.most_common(5)])

# 桶内条目的 hash 是否成段（验证分组=按 hash 分区）
for i in range(3):
    grp = [arr[cum[i] + j] for j in range(bk[i][1])]
    hs = [byT[p][1] for p in grp if p in byT]
    print('桶%d 条数%d hash: %s' % (i, bk[i][1], ['0x%08X' % h for h in hs]))

# 全表 hash 是否有序（按数组顺序）
hs_all = [byT[p][1] for p in arr if p in byT]
print('数组顺序 hash 单调?', all(hs_all[i] < hs_all[i+1] for i in range(len(hs_all)-1)))
# 桶号 vs hash 高位
if all(arr[cum[i]] in byT for i in range(128)):
    first_h = [byT[arr[cum[i]]][1] for i in range(128)]
    for sh in (24, 25, 26, 27):
        print('桶号==hash>>%d: %d/128' % (sh, sum(1 for i, h in enumerate(first_h) if h >> sh == i)))
    print('样例:', [(i, '0x%08X' % h, h >> 24) for i, h in enumerate(first_h[:6])])
