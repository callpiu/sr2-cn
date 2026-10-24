# -*- coding: utf-8 -*-
"""正确解析 static_CH.le_strings：
头: magic(4)=0xA84C7F73, ver(4), count(4)=12250
然后 count 条 (u32 a, u32 b)
字符串池从某 offset 开始，每串 UTF-16 (slot)，以 0x0000 结束
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
print('magic=%08X ver=%d count=%d' % (magic, ver, count))

# 接下来 count 条 (u32,u32)
recs = []
for i in range(count):
    a, b = struct.unpack_from('<II', raw, 12 + i*8)
    recs.append((a, b))
print('first 6 recs:', [(hex(a), hex(b)) for a, b in recs[:6]])
print('last rec:', [(hex(a), hex(b)) for a, b in recs[-2:]])

# 判断哪个是 hash，哪个是 offset
# hash 通常大且分散；offset 递增且小(<文件大小)
offs = [b for a, b in recs]
hs = [a for a, b in recs]
print('offsets 范围: %d..%d  min=%d' % (min(offs), max(offs), min(offs)))
print('as 范围: %d..%d  0x%X..0x%X' % (min(hs), max(hs), min(hs), max(hs)))

# 取一个 offset 试解 UTF-16
def read_str(off):
    o = off
    out = []
    while o + 1 < len(raw):
        u = struct.unpack_from('<H', raw, o)[0]
        o += 2
        if u == 0:
            break
        if 0x20 <= u <= 0x7E:
            out.append(chr(u))
        else:
            i = u - 0x20
            out.append(chr(cn[i]) if 0 <= i < LE else '<%#x>' % u)
    return ''.join(out)

# 用 rec 0 和找 REC1
for i in (0, 1, 2, 4717 - 1):
    a, b = recs[i]
    print('rec[%d] a=%08X b=%d: %s' % (i, a, b, read_str(b)[:60]))

# 直接找 REC1 hash 0x84F287ED
for i, (a, b) in enumerate(recs):
    if a == 0x84F287ED:
        print('REC1 at rec %d offset=%d:' % (i, b), read_str(b))
        break
for i, (a, b) in enumerate(recs):
    if a == 0x10AF1E62:
        print('REC2 at rec %d offset=%d:' % (i, b), read_str(b))
        break
