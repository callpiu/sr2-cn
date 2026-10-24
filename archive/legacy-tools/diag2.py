# -*- coding: utf-8 -*-
# 决定性验证：static_CH 是否 slot 制；坏记录 slot 反解是否 = 截图乱码字
import struct, sys
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
sys.stdout.reconfigure(encoding="utf-8")

V531 = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc.v531_before_mirror.bak"
vpp = Vpp(V531)
CPS = [int(l) for l in vpp.read(vpp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
N = len(CPS)
print(f"charlist_CH: {N} 项, 前10={CPS[:10]}, 最大=0x{max(CPS):X}")
cp2idx = {}
for i, c in enumerate(CPS):
    cp2idx.setdefault(c, i)

def parse_le(blob):
    magic, ver, nb, count = struct.unpack_from('<IHHI', blob, 0)
    A0 = 12 + nb*8
    offs = struct.unpack_from('<%dI' % count, blob, A0)
    out = {}
    for off in offs:
        id1, id2 = struct.unpack_from('<HH', blob, off)
        h = (id1 << 16) | id2
        sp = off + 4
        txt = []
        while True:
            (u,) = struct.unpack_from('>H', blob, sp)
            if u == 0: break
            txt.append(u); sp += 2
        out[h] = (off, txt)
    return out

ch = parse_le(bytes(vpp.read(vpp.find("static_CH", "le_strings"))))
us = parse_le(bytes(vpp.read(vpp.find("static_US", "le_strings"))))

def slot_decode(txt):
    return ''.join(chr(CPS[v-0x20]) if 0x20 <= v-0x20 < N else f'[{v:04X}]' for v in txt)

for h in (0x84F287ED, 0x10AF1E62):
    off, txt = ch[h]
    print(f"\n=== hash 0x{h:08X} @0x{off:X}")
    print(f"  raw u16 ({len(txt)}): {[hex(v) for v in txt]}")
    print(f"  slot反解: {slot_decode(txt)!r}")
    if h in us:
        print(f"  US 原文 : {(''.join(chr(c) for c in us[h][1]))!r}")

# 对照组：全表 slot 反解统计——多少记录反解出非法 slot / 含 CJK
bad_range = 0; has_cjk = 0; total = 0
for h, (off, txt) in ch.items():
    total += 1
    oob = [v for v in txt if v >= 0x20 and not (0x20 <= v-0x20 < N)]
    if oob: bad_range += 1
    if any(0x4E00 <= CPS[v-0x20] <= 0x9FFF for v in txt if 0x20 <= v-0x20 < N): has_cjk += 1
print(f"\n全表普查: {total} 条, slot越界记录={bad_range}, 反解含CJK={has_cjk}")
