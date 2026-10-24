# -*- coding: utf-8 -*-
import struct
G = 'G:/SteamLibrary/steamapps/common/Saints Row 2/DLC/Text/'
raw = open(G + 'dlc_us.le_strings', 'rb').read()

TEXT0 = 0x1364          # 文本区起点（首条 hash 在此）
ARR0, ARRN = 0x40C, 982 # 索引数组
BKT0, BKTN = 0x08, 128  # 桶表

# 1) 解析文本区
ents = []   # (offset, hash, text, nchars)
o = TEXT0
while o + 4 <= len(raw):
    h = struct.unpack_from('>I', raw, o)[0]
    o += 4
    cps = []
    while o + 2 <= len(raw):
        u = struct.unpack_from('>H', raw, o)[0]
        o += 2
        if u == 0:
            break
        cps.append(u)
    ents.append((o, h, ''.join(chr(c) for c in cps), len(cps)))
    if o + 4 > len(raw):
        break
print('文本区条目数', len(ents), ' 末尾 offset', hex(ents[-1][0]), ' 文件大小', len(raw))

# 2) 索引数组
arr = [struct.unpack_from('<I', raw, ARR0 + i * 4)[0] for i in range(ARRN)]
offs = set(e[0] - 4 for e in ents)          # 每条记录的起始(hash 处)
print('数组最小值', hex(min(arr)), '最大值', hex(max(arr)))
print('数组元素都是某条目的起始偏移?', all(a in offs for a in arr))
print('数组严格递减?', all(arr[i] > arr[i+1] for i in range(len(arr)-1)))

# 3) 数组顺序 vs hash 排序
by_hash_desc = sorted(ents, key=lambda e: -e[1])
by_hash_asc = sorted(ents, key=lambda e: e[1])
seq_desc = [e[0] - 4 for e in by_hash_desc]
seq_asc = [e[0] - 4 for e in by_hash_asc]
print('数组 == 按 hash 降序的偏移序列?', arr == seq_desc)
print('数组 == 按 hash 升序的偏移序列?', arr == seq_asc)

# 4) 桶表：假设 pair = (offset, len)，offset 相对什么？
bk = [struct.unpack_from('<II', raw, BKT0 + i * 8) for i in range(BKTN)]
def try_base(name, base):
    ok = 0
    for off, ln in bk:
        p = base + off
        if p in offs:
            e = next(x for x in ents if x[0] - 4 == p)
            if e[3] == ln:
                ok += 1
    print('%s: 命中 %d/%d' % (name, ok, BKTN))
try_base('绝对偏移', 0)
try_base('相对文本区(0x1364)', TEXT0)
try_base('相对数组(0x40C)', ARR0)

# 5) 桶索引规则：pair 对应的条目 hash → 桶号
if all((TEXT0 + off) in offs for off, ln in bk):
    hs = []
    for i, (off, ln) in enumerate(bk):
        e = next(x for x in ents if x[0] - 4 == TEXT0 + off)
        hs.append((i, e[1]))
    for shift in (24, 25, 26):
        good = sum(1 for i, h in hs if (h >> shift) == i)
        print('桶号 == hash>>%d : %d/%d' % (shift, good, BKTN))
    good = sum(1 for i, h in hs if (h % 128) == i)
    print('桶号 == hash%%128 : %d/%d' % (good, BKTN))
    print('样例(桶号, hash, hash>>24, hash&0xFF):',
          [(i, '0x%08X' % h, h >> 24, h & 0xFF) for i, h in hs[:8]])
