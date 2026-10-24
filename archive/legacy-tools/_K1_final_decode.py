# -*- coding: utf-8 -*-
"""最终解码器：
le_strings(v2) = magic(4) + ver(2) + buckets(2) + count(4)
                 + count * u32 (offset表, 位于 16+buckets*8)
                 记录体 = <u16 hash> <u16 pad> <UTF-16BE 文本> <u16 0x0000>
unit 值 >0xFF 时用 charlist 映射（CL[u]）
"""
import sys, struct, os
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp
from sr2strings import CharList

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(G + '/patch.vpp_pc')
txt = v.read(v.find('charlist_CH', 'txt')).decode()
ns = [int(t) for t in txt.split() if t.lstrip('-').isdigit()]
if ns and ns[0] == len(ns) - 1:
    ns = ns[1:]
CL = CharList(ns)

def decode_file(raw, cl):
    magic, ver, buckets, count = struct.unpack_from('<IHHI', raw, 0)
    off_at = 16 + buckets * 8
    out = []
    for i in range(count):
        if off_at + i * 4 + 4 > len(raw):
            break
        o = struct.unpack_from('<I', raw, off_at + i * 4)[0]
        if not (0 <= o < len(raw) - 4):
            continue
        h = struct.unpack_from('<H', raw, o)[0]
        p = o + 4
        chars = []
        ok = True
        while p + 1 < len(raw):
            u = struct.unpack_from('>H', raw, p)[0]
            p += 2
            if u == 0:
                break
            if u < 0x100:
                chars.append(chr(u))
            elif u < len(cl.body):
                chars.append(chr(cl.body[u]))
            else:
                chars.append('<?%d>' % u)
                ok = False
            if len(chars) > 800:
                break
        out.append((h, ''.join(chars)))
    return ver, buckets, count, out

for nm in ['static_CH', 'voice_script_CH', 'platform_pc_CH']:
    try:
        raw = v.read(v.find(nm, 'le_strings'))
    except Exception as e:
        print(nm, 'ERR', e)
        continue
    ver, buckets, count, recs = decode_file(raw, CL)
    print('=== %s ver=%d buckets=%d count=%d 解码=%d ===' % (nm, ver, buckets, count, len(recs)))
    # 统计可读率
    good = sum(1 for _, s in recs if s and all(c.isprintable() or c == '?' for c in s))
    print('   可读记录=%d' % good)
    KEYS = ['直升机', '突击', '弟兄们', '保护', '面包车', '停靠', '生意', '迷雾巷', '你的']
    hits = [(h, s) for h, s in recs if any(k in s for k in KEYS)]
    print('   关键字命中=%d' % len(hits))
    for h, s in hits[:25]:
        print('      h=%04X  %s' % (h, s[:80]))
