# -*- coding: utf-8 -*-
"""完整解码器：
le_strings: magic(4)+ver(4)+count(4); count 条 (u32 hash, u32 tbl_off)
tbl_off 指向 u32 数组；数组每项指向记录体：<u32 hash><UTF-16LE str 0x0000>
用 charlist 把 >0x7E 的码点映射（CH 表）
"""
import struct, os, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(os.path.join(G, 'patch.vpp_pc'))
CL = [int(x) for x in v.read(v.find('charlist_CH', 'txt')).decode('utf-8').split('\n') if x.strip().isdigit()]
CLMAP = {0x20 + i: c for i, c in enumerate(CL)}
print('CL len=%d' % len(CL))

def dec_str_at(raw, off):
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
            c = CLMAP.get(u)
            out.append(chr(c) if c else '{U+%04X}' % u)
    return ''.join(out)

def load(p):
    raw = open(p, 'rb').read()
    magic, ver, count = struct.unpack_from('<III', raw, 0)
    idx = {}
    for i in range(count):
        h, tbloff = struct.unpack_from('<II', raw, 12 + i * 8)
        if tbloff == 0xFFFFFFFF or tbloff == 0 or tbloff >= len(raw):
            continue
        # 该记录的字符串数组
        n = struct.unpack_from('<I', raw, tbloff)[0]
        if n > 200:
            # 可能 tbloff 直接指向记录体
            s = dec_str_at(raw, tbloff + 4)
            idx[h] = [s]
            continue
        arr = []
        for k in range(n):
            sub = struct.unpack_from('<I', raw, tbloff + 4 + k * 4)[0]
            arr.append(dec_str_at(raw, sub + 4))
        idx[h] = arr
    return raw, magic, ver, count, idx

for p in [os.path.join(G, 'Mods', 'static_US.le_strings')]:
    raw, magic, ver, count, idx = load(p)
    print('===', os.path.basename(p), 'count=', count, 'entries=', len(idx))
    for h in list(idx)[:5]:
        print('   h=%08X -> %r' % (h, idx[h][:3]))

# CH 表
raw = v.read(v.find('static_CH', 'le_strings'))
print('=== patch.vpp_pc/static_CH.le_strings size=', len(raw))
open('F:/sr2-cn/_static_CH_raw.bin', 'wb').write(raw)
magic, ver, count = struct.unpack_from('<III', raw, 0)
print('magic=%08X ver=%d count=%d' % (magic, ver, count))
for i in range(3):
    h, tbloff = struct.unpack_from('<II', raw, 12 + i * 8)
    print('   rec%d h=%08X tbloff=%d' % (i, h, tbloff))
