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
byR = {e[0]: e for e in ents}
byT = {e[0] + 4: e for e in ents}
arr = [struct.unpack_from('<I', raw, 0x408 + i * 4)[0] for i in range(982)]

# 数组 = 文本指针表？是否按 hash 排序
hit = sum(1 for a in arr if a in byT)
print('数组命中文本起点', hit, '/982')
hs = [byT[a][1] for a in arr if a in byT]
print('按 hash 降序?', all(hs[i] > hs[i+1] for i in range(len(hs)-1)))
print('按 hash 升序?', all(hs[i] < hs[i+1] for i in range(len(hs)-1)))
print('hash 头 5:', ['0x%08X' % h for h in hs[:5]])
print('hash 尾 5:', ['0x%08X' % h for h in hs[-5:]])

# 桶表：pair=(off,len)，off 指向文本起点？
bk = [struct.unpack_from('<II', raw, 0x08 + i * 8) for i in range(128)]
for bname, base in [('abs', 0), ('+4', 4), ('+TEXT0', TEXT0), ('+TEXT0+4', TEXT0 + 4)]:
    ok = 0
    for off, ln in bk:
        p = base + off
        if p in byT and byT[p][3] == ln:
            ok += 1
    print('桶表 base %-9s 命中 %d/128' % (bname, ok))

# 桶表 pair 指向 hash 起点？
for bname, base in [('abs', 0), ('-4', -4), ('+TEXT0', TEXT0), ('+TEXT0-4', TEXT0 - 4)]:
    ok = 0
    for off, ln in bk:
        p = base + off
        if p in byR and byR[p][3] == ln:
            ok += 1
    print('桶表(hash起点) base %-9s 命中 %d/128' % (bname, ok))

# 桶表 off 与数组值的关系：off 是否等于 数组中的某个值？
aset = set(arr)
print('桶表 off 落在数组值内:', sum(1 for off, ln in bk if off in aset), '/128')
# 桶表 off 是否 == 数组字节偏移(绝对)
apos = {0x408 + i * 4: i for i in range(982)}
print('桶表 off 落在数组字节地址内:', sum(1 for off, ln in bk if off in apos), '/128')
# 桶表第二字段累加
print('桶表 len 总和', sum(ln for off, ln in bk))
