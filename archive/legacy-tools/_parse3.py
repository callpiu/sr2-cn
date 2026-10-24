# -*- coding: utf-8 -*-
"""用正确的 le_strings 结构解析 static_CH（游戏当前加载的 patch.vpp_pc），
解码 REC1/REC2，并用多张字表交叉验证，定位乱码根因。
"""
import sys, os, struct, re
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'


def load_charlist(vp, name):
    e = vp.find(name, 'txt')
    buf = vp.read(e)
    end = buf.find(b'//ENDOFFILE')
    if end < 0:
        end = len(buf)
    return [int(x) for x in re.findall(rb'\d+', buf[:end])]


def parse_le(data):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', data, 0)
    assert magic == 0xA84C7F73, hex(magic)
    off = 12
    btab = []
    for i in range(buckets):
        cnt, addr = struct.unpack_from('<II', data, off)
        off += 8
        btab.append((cnt, addr))
    ptrs = []
    for i in range(count):
        ptrs.append(struct.unpack_from('<I', data, off)[0])
        off += 4
    return magic, ver, buckets, count, btab, ptrs


def decode_record(data, off, cl):
    id1, id2 = struct.unpack_from('<HH', data, off)
    p = off + 4
    chars = []
    slots = []
    while p + 2 <= len(data):
        s = struct.unpack_from('>H', data, p)[0]   # UTF-16BE on disk
        if s == 0:
            break
        slots.append(s)
        p += 2
        if s < 0x20:
            chars.append('<%02X>' % s)
        else:
            ci = s - 0x20
            chars.append(chr(cl[ci]) if 0 <= ci < len(cl) else '<%d>' % s)
    return (id1, id2), chars, slots


vp = Vpp(os.path.join(G, 'patch.vpp_pc'))
cl = load_charlist(vp, 'charlist_CH')
print('charlist_CH entries:', len(cl))

data = vp.read(vp.find('static_CH', 'le_strings'))
magic, ver, buckets, count, btab, ptrs = parse_le(data)
print('magic=%08X ver=%d buckets=%d count=%d' % (magic, ver, buckets, count))
print('buckets head:', btab[:4])

# REC1/REC2
for target in (0x84F287ED, 0x10AF1E62):
    for off in ptrs:
        if off == 0 or off >= len(data):
            continue
        (id1, id2), chars, slots = decode_record(data, off, cl)
        if (id1 << 16) | id2 == target:
            print('\n=== hash %08X (rec off %d) ===' % (target, off))
            print('text:', ''.join(chars))
            cjk = [(c, s) for c, s in zip(chars, slots) if s >= 0x100]
            print('CJK count=%d' % len(cjk))
            print('  ' + ' '.join('%s(s=%d)' % (c, s) for c, s in cjk))
            break
