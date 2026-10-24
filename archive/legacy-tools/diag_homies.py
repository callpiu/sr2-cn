# -*- coding: utf-8 -*-
# 诊断：v531(原版) static_CH/voice_script_CH 中目标 hash 的全部记录 + 重复 hash 普查
import struct, sys
from collections import defaultdict

V531 = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc.v531_before_mirror.bak"
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp

def parse_le(blob):
    magic, ver, nb, count = struct.unpack_from('<IHHI', blob, 0)
    assert magic == 0x6C656853 or True, hex(magic)
    A0 = 12 + nb*8
    offs = struct.unpack_from('<%dI' % count, blob, A0)
    recs = []  # (ptr_array_idx, off, hash, text_u16_list)
    for i, off in enumerate(offs):
        id1, id2 = struct.unpack_from('<HH', blob, off)
        h = (id1 << 16) | id2
        sp = off + 4
        txt = []
        while True:
            (u,) = struct.unpack_from('>H', blob, sp)
            if u == 0: break
            txt.append(u); sp += 2
        recs.append((i, off, h, txt))
    return nb, count, recs

def txt_str(u16s):
    return ''.join(chr(c) for c in u16s)

vpp = Vpp(V531)

targets_txt = ['homies', 'heading out']
for us_n, ch_n in [('static_US','static_CH'), ('voice_script_US','voice_script_CH')]:
    print('='*70)
    for name in (us_n, ch_n):
        e = vpp.find(name, 'le_strings')
        blob = vpp.read(e)
        nb, count, recs = parse_le(blob)
        # 重复 hash 普查
        dh = defaultdict(list)
        for (i, off, h, txt) in recs:
            dh[h].append((i, off, txt))
        dups = {h: v for h, v in dh.items() if len(v) > 1}
        print(f'--- {name}: nb={nb} count={count} 重复hash数={len(dups)} 涉及记录数={sum(len(v) for v in dups.values())}')
        # 目标文本搜索
        for (i, off, h, txt) in recs:
            s = txt_str(txt)
            low = s.lower()
            if any(t in low for t in targets_txt):
                print(f'  [文本命中] hash=0x{h:08X} off=0x{off:X} ptrIdx={i} len={len(txt)}')
                print(f'    text={s[:80]!r}')
                print(f'    u16={[hex(c) for c in txt[:40]]}')
        # 指定 hash 的全部记录
        for hh in (0x84F287ED,):
            if hh in dh:
                for (i, off, txt) in dh[hh]:
                    print(f'  [hash 0x{hh:08X}] off=0x{off:X} ptrIdx={i} text={txt_str(txt)[:80]!r}')
            else:
                print(f'  [hash 0x{hh:08X}] 不存在于 {name}')
