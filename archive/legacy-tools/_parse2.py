# -*- coding: utf-8 -*-
"""le_strings 结构定案：
  0x00 magic 0xA84C7F73
  0x04 version
  0x08 count = 12250
  0x0C: count × (u32 hash, u32 len)          # 12 + 8*12250 = 0x17F3C
  然后:  offset table (u32) × count? 或 len 表
  然后:  字符串池（每串 = len 个 u16 slot，无终止符？）
"""
import sys, os, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(os.path.join(G, 'patch.vpp_pc'))
cn = [int(l) for l in v.read(v.find('charlist_CH', 'txt')).decode('utf-8', 'replace').split('\n') if l.strip().isdigit()]
LE = len(cn)
raw = v.read(v.find('static_CH', 'le_strings'))
magic, ver, count = struct.unpack('<III', raw[:12])
print('magic=%08X ver=%08X count=%d' % (magic, ver, count))

TBL = 12
ent = []
for i in range(count):
    h, l = struct.unpack_from('<II', raw, TBL + i*8)
    ent.append((h, l))
print('table end = 0x%X' % (TBL + count*8))
print('first 4 (hash,len):', [(hex(h), l) for h, l in ent[:4]])
print('last 4 (hash,len):', [(hex(h), l) for h, l in ent[-4:]])

# hash 是否升序？
asc = all(ent[i][0] <= ent[i+1][0] for i in range(count-1))
print('hash 升序:', asc)

# 找 REC1 hash
for i, (h, l) in enumerate(ent):
    if h == 0x84F287ED:
        print('REC1 idx=%d len=%d' % (i, l))
        rec1i = i
        break
for i, (h, l) in enumerate(ent):
    if h == 0x10AF1E62:
        print('REC2 idx=%d len=%d' % (i, l))
        rec2i = i
        break

# 假设：table 后面紧跟 count 个 u32 偏移
after = TBL + count*8
print('after table @0x%X, first u32s: %s' % (after, struct.unpack_from('<8I', raw, after)))
