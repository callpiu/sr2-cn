# -*- coding: utf-8 -*-
"""正确模型：magic(4) + ver(4) + count(4)  然后 count 条 <u32 hash><u32 off>
字符串池从 12+count*8 开始，UTF-16LE，0x0000 结束
slot 体系：charlist_CH.txt（2795 项，CL[0]=0x20）
"""
import struct, os, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
M = os.path.join(G, 'Mods')
S = os.path.join(G, 'Mods', 'JUICED - Strings')

v = Vpp(os.path.join(G, 'patch.vpp_pc'))
CL = [int(x) for x in v.read(v.find('charlist_CH', 'txt')).decode('utf-8').split('\n') if x.strip().isdigit()]
print('CL len=%d CL[0]=%d' % (len(CL), CL[0]))

def parse(p):
    raw = open(p, 'rb').read()
    magic, ver, count = struct.unpack_from('<III', raw, 0)
    base = 12
    recs = []
    for i in range(count):
        h, off = struct.unpack_from('<II', raw, base + i * 8)
        recs.append((h, off))
    return raw, magic, ver, count, recs

def decode(raw, off, mode):
    out = []
    o = off
    while o + 1 < len(raw):
        u = struct.unpack_from('<H', raw, o)[0]
        o += 2
        if u == 0:
            break
        if 0x20 <= u <= 0x7E:
            out.append(chr(u))
        else:
            i = u - 0x20 if mode == 'sub' else u
            out.append(chr(CL[i]) if 0 <= i < len(CL) else '{%d}' % u)
    return ''.join(out)

for p in [os.path.join(M, 'static_US.le_strings'),
          os.path.join(M, 'static_JP.le_strings'),
          os.path.join(S, 'patch_ch.le_strings'),
          os.path.join(S, 'juiced_CH.le_strings')]:
    raw, magic, ver, count, recs = parse(p)
    print('=' * 70)
    print('%s magic=%08X ver=%d count=%d' % (os.path.basename(p), magic, ver, count))
    # 抽样
    for i in [0, 1, 2, 100]:
        if i >= len(recs):
            break
        h, off = recs[i]
        print('  rec%d h=%08X off=%d  sub:%r' % (i, h, off, decode(raw, off, 'sub')[:50]))
    for tgt, tag in [(0x84F287ED, 'REC1'), (0x10AF1E62, 'REC2')]:
        hit = [r for r in recs if r[0] == tgt]
        if hit:
            print('  %s h=%08X off=%d  sub:%r' % (tag, tgt, hit[0][1], decode(raw, hit[0][1], 'sub')[:70]))
        else:
            print('  %s NOT FOUND' % tag)
