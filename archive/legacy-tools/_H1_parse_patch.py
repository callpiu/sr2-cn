# -*- coding: utf-8 -*-
"""重新解析 le_strings：模型假设 =
magic(4) + u16 ver + u16 num_entries + 每条记录: u32 hash + u16 槽位序列(以 0xFFFF 或 0x0000 结尾)
先做结构探测。"""
import struct, os, json

D = r'G:\SteamLibrary\steamapps\common\Saints Row 2\Mods\JUICED - Strings'
FILES = ['patch_ch.le_strings', 'patch_us.le_strings', 'juiced_CH.le_strings']

for fn in FILES:
    p = os.path.join(D, fn)
    raw = open(p, 'rb').read()
    print('='*70)
    print('%s  size=%d' % (fn, len(raw)))
    magic, ver, cnt = struct.unpack_from('<IHH', raw, 0)
    print('  magic=%08X ver=%d cnt=%d' % (magic, ver, cnt))
    # dump 前 64 字节按 u16
    u16s = struct.unpack_from('<32H', raw, 0)
    print('  u16[0:32]=', u16s)
    # 尝试：从 offset 8 开始，按 hash(4) + slots 走到 0xFFFF 结束
    off = 8
    print('  --- 试解析 ---')
    n = 0
    while off + 4 <= len(raw) and n < 6:
        h = struct.unpack_from('<I', raw, off)[0]
        off += 4
        slots = []
        while off + 2 <= len(raw) and len(slots) < 200:
            s = struct.unpack_from('<H', raw, off)[0]
            off += 2
            if s == 0xFFFF:
                break
            if s == 0 and len(slots) == 0:
                break
            slots.append(s)
        print('   rec%d hash=%08X slots(%d)=%s' % (n, h, len(slots), slots[:20]))
        n += 1
