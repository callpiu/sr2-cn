# -*- coding: utf-8 -*-
"""假设：hdr16 + count*(u32 hash, u32 len) 紧跟数据区。
数据区起点 = 16 + count*8。检查该处内容，并按 len 顺序切分解码。
"""
import sys, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp
from sr2strings import CharList

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(G + '/patch.vpp_pc')
raw = v.read(v.find('static_CH', 'le_strings'))
txt = v.read(v.find('charlist_CH', 'txt')).decode()
ns = [int(t) for t in txt.split() if t.lstrip('-').isdigit()]
if ns and ns[0] == len(ns) - 1:
    ns = ns[1:]
CL = CharList(ns)

magic, ver, buckets, count = struct.unpack_from('<IHHI', raw, 0)
print('magic=%08X ver=%d buckets=%d count=%d' % (magic, ver, buckets, count))
print('16+count*8 =', 16 + count * 8, 'filesize=', len(raw))
print('96+count*8 =', 96 + count * 8)

for base in (16 + count * 8, 16 + buckets * 8, 96 + count * 8):
    if base >= len(raw):
        print('base=%d OOB' % base)
        continue
    print('base=%d head=%s' % (base, raw[base:base + 24].hex()))
    sample = [(struct.unpack_from('<I', raw, base + i * 8)[0],
               struct.unpack_from('<I', raw, base + i * 8 + 4)[0]) for i in range(4)]
    print('   pairs:', [(hex(a), b) for a, b in sample])
    # 第一对的 len 是否合理
