# -*- coding: utf-8 -*-
# 普查：static_CH / voice_script_CH / platform_pc_CH 中「slot 值混入码点表」的坏记录
import struct, sys
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
sys.stdout.reconfigure(encoding="utf-8")

V531 = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc.v531_before_mirror.bak"
vpp = Vpp(V531)
CPS = [int(l) for l in vpp.read(vpp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
N = len(CPS)
cp2idx = set(CPS)

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

def bad_vals(txt):
    # 码点制下引擎无法解析的值 = 不在 charlist 且非 ASCII 且非 CJK 兼容区
    out = []
    for v in txt:
        if v in cp2idx: continue          # 码点在字表里 → 正常
        if 0x20 <= v-0x20 < N and CPS[v-0x20] >= 0x80:
            out.append(v)                 # slot 值误入（反解出非 ASCII 字）
        else:
            out.append(v)                 # 其他不可解析值
    return out

for name in ("static_CH", "voice_script_CH", "platform_pc_CH"):
    try:
        e = vpp.find(name, "le_strings")
    except Exception as ex:
        print(f"{name}: 找不到 ({ex})"); continue
    ch = parse_le(bytes(vpp.read(e)))
    broken = []
    for h, (off, txt) in ch.items():
        bv = bad_vals(txt)
        if bv:
            broken.append((h, off, txt, bv))
    print(f"=== {name}: {len(ch)} 条, 坏记录 {len(broken)} 条")
    for h, off, txt, bv in broken:
        dec = ''.join(chr(CPS[v-0x20]) if (v not in cp2idx and 0x20 <= v-0x20 < N)
                      else chr(v) for v in txt)
        print(f"  0x{h:08X} @0x{off:X} 坏值={[hex(x) for x in bv]}")
        print(f"    修复后应读作: {dec!r}")
