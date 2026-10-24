# -*- coding: utf-8 -*-
# 决定性诊断：表的真实编码是码点还是 slot？
# 1) 搜索已知正常记录「面包车耐久」的原始字节(码点)以确认引擎用码点
# 2) 用码点解法普查：哪些记录的中文被写成了 slot 值(误编码)
import struct, sys
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
sys.stdout.reconfigure(encoding="utf-8")

V531 = r"G:\SteamLibrary\steamapps\common\Saints Row 2\patch.vpp_pc.v531_before_mirror.bak"
vp = Vpp(V531)
CPS = [int(l) for l in vp.read(vp.find("charlist_CH", "txt"))
       .decode("utf-8").split("\n") if l.strip().isdigit()]
N = len(CPS)

def parse_le(blob):
    magic, ver, nb, count = struct.unpack_from('<IHHI', blob, 0)
    A0 = 12 + nb*8
    offs = struct.unpack_from('<%dI' % count, blob, A0)
    recs = []
    for off in offs:
        id1, id2 = struct.unpack_from('<HH', blob, off)
        h = (id1 << 16) | id2
        sp = off + 4
        txt = []
        while True:
            (u,) = struct.unpack_from('>H', blob, sp)
            if u == 0: break
            txt.append(u); sp += 2
        recs.append((off, h, txt))
    return recs

# 1) 确认「面包车耐久」是码点制：搜索 UTF-16BE 码点序列
target_str = "面包车耐久"
target_be = b''.join(u16.to_bytes(2,'big') for u16 in [ord(c) for c in target_str])
whole_patch = vp.data
pos = whole_patch.find(target_be)
print(f"在 patch 内搜索码点'面包车耐久' UTF-16BE: {'找到 @0x%X' % pos if pos>=0 else '未找到'}")
# 也搜 slot 形式：每个字 = idx+0x20，先找这些字在 CPS 中的 idx
idx_target = [CPS.index(ord(c)) for c in target_str if ord(c) in CPS]
slot_be = b''.join((i+0x20).to_bytes(2,'big') for i in idx_target) if idx_target else b''
pos2 = whole_patch.find(slot_be)
print(f"搜索 slot 形式'面包车耐久': {'找到 @0x%X' % pos2 if pos2>=0 else '未找到'}")

# 2) 普查：码点解法下，哪些记录的 CJK 被写成 slot
def is_cjk_codepoint(v): return 0x4E00 <= v <= 0x9FFF
def is_slot_cjk(v):
    # 值落在 [0x20,0x4E00) 且作为 slot 解出是 CJK -> 误编码
    return 0x20 <= v-0x20 < N and is_cjk_codepoint(CPS[v-0x20])

for name in ("static_CH","voice_script_CH"):
    blob = bytes(vp.read(vp.find(name,"le_strings")))
    recs = parse_le(blob)
    slot_records = []
    for off,h,txt in recs:
        bad = [v for v in txt if is_slot_cjk(v)]
        if bad:
            # 码点解 vs 修正后码点
            cur = ''.join(chr(v) for v in txt)
            fixed = ''.join(chr(CPS[v-0x20]) if is_slot_cjk(v) else chr(v) for v in txt)
            slot_records.append((h,off,bad,cur,fixed))
    print(f"\n=== {name}: 误编码(slot)记录 {len(slot_records)} 条 / 共 {len(recs)}")
    for h,off,bad,cur,fixed in slot_records[:40]:
        print(f"  0x{h:08X} @0x{off:X} 坏值数={len(bad)}  修正后={fixed[:40]!r}")
