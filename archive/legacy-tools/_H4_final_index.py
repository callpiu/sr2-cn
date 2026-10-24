# -*- coding: utf-8 -*-
"""终局验证：
1) 从 patch.vpp_pc 取 charlist_CH.txt -> CL (2795, CL[0]=0x20)
2) 解析 Mods/JUICED - Strings/patch_ch.le_strings 与 patch_us.le_strings
   结构：u16[0:4]=magic_lo,magic_hi,ver,cnt; 之后逐记录
3) 用 idx = slot-0x20 解码，看是否得到英文原文（patch_us 已知是英文）
   若 patch_us 能解出可读英文 => 索引模型正确，进而检查 patch_ch 是否被损坏
"""
import struct, os, sys
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
S = os.path.join(G, 'Mods', 'JUICED - Strings')

v = Vpp(os.path.join(G, 'patch.vpp_pc'))
raw = v.read(v.find('charlist_CH', 'txt'))
CL = [int(x) for x in raw.decode('utf-8').split('\n') if x.strip().isdigit()]
print('CL len=%d  CL[0]=%d(0x%X) CL[1]=%d CL[224]=%d' % (len(CL), CL[0], CL[0], CL[1], CL[224]))

def dec(slots, base):
    out = []
    for s in slots:
        i = s - base
        out.append(chr(CL[i]) if 0 <= i < len(CL) else '<?%d>' % s)
    return ''.join(out)

def parse_records(path):
    raw = open(path, 'rb').read()
    magic_lo, magic_hi, ver, cnt = struct.unpack_from('<4H', raw, 0)
    recs = []
    off = 8
    while off + 8 <= len(raw):
        h = struct.unpack_from('<I', raw, off)[0]
        off += 4
        n = struct.unpack_from('<I', raw, off)[0]
        off += 4
        if n > 5000:
            break
        slots = list(struct.unpack_from('<%dI' % n, raw, off))
        off += n * 4
        # 跳过终止 0 / FFFFFFFF
        while off + 4 <= len(raw):
            t = struct.unpack_from('<I', raw, off)[0]
            if t in (0, 0xFFFFFFFF):
                off += 4
            else:
                break
        recs.append((h, slots))
    return magic_lo, magic_hi, ver, cnt, recs

for fn in ['patch_us.le_strings', 'patch_ch.le_strings', 'juiced_US.le_strings', 'juiced_CH.le_strings']:
    p = os.path.join(S, fn)
    a, b, ver, cnt, recs = parse_records(p)
    print('=' * 70)
    print('%s magic=%04X%04X ver=%d cnt=%d parsed_recs=%d' % (fn, b, a, ver, cnt, len(recs)))
    for h, slots in recs[:8]:
        print('  h=%08X n=%2d  slot-0x20: %r' % (h, len(slots), dec(slots, 0x20)))
        print('  %s        slot      : %r' % (' ' * 12, dec(slots, 0)))
