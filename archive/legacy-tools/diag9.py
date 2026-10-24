# -*- coding: utf-8 -*-
# 检查：1) patch_ch.le_strings 内容与 hash 2) 面包车耐久所属表 3) 各表 header ver
import struct, sys, os
sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
V531 = G + r"\patch.vpp_pc.v531_before_mirror.bak"

def parse_le_hdr(blob):
    magic, ver, nb, count = struct.unpack_from('<IHHI', blob, 0)
    return magic, ver, nb, count

def parse_le(blob):
    magic, ver, nb, count = parse_le_hdr(blob)
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
    return ver, nb, out

# 1) patch_ch.le_strings (Juiced loose)
p = G + r"\Mods\JUICED - Strings\patch_ch.le_strings"
blob = open(p, 'rb').read()
print(f"patch_ch.le_strings: {len(blob)} B, magic=0x{struct.unpack_from('<I',blob,0)[0]:08X}, ver={struct.unpack_from('<H',blob,4)[0]}, nb={struct.unpack_from('<H',blob,6)[0]}, count={struct.unpack_from('<I',blob,8)[0]}")
# 也看 patch_us 对比
pu = open(G + r"\Mods\JUICED - Strings\patch_us.le_strings", 'rb').read()
print(f"patch_us.le_strings: {len(pu)} B, magic=0x{struct.unpack_from('<I',pu,0)[0]:08X}")
try:
    ver, nb, recs = parse_le(blob)
    print(f"  patch_ch 解析: {len(recs)} 条")
    for h in (0x84F287ED, 0x10AF1E62):
        print(f"  hash 0x{h:08X} in patch_ch? {h in recs}")
    # 打印前5条原文(u16 hex)
    for i,(h,(off,txt)) in enumerate(recs.items()):
        if i>=5: break
        print(f"    0x{h:08X}: {[hex(v) for v in txt[:12]]}")
except Exception as ex:
    print(f"  解析失败: {ex}")

# 2) 面包车耐久 @文件0x1C6B030 属于哪个表
vp = Vpp(V531)
target_off = 0x1C6B030
for e in vp.entries():
    body_start = vp.data_start + e['body']
    if body_start <= target_off < body_start + e['size']:
        print(f"\n'面包车耐久'@0x{target_off:X} 位于条目 {e['name']}.{e['ext']} (body@0x{body_start:X}, size={e['size']})")
        rel = target_off - body_start
        print(f"  表内相对偏移=0x{rel:X}")

# 3) 各表 header ver
for name in ("static_US","static_CH","voice_script_US","voice_script_CH","platform_pc_US","platform_pc_CH"):
    e = vp.find(name, "le_strings")
    if e:
        b = bytes(vp.read(e))
        magic, ver, nb, count = parse_le_hdr(b)
        print(f"{name}: ver={ver} nb={nb} count={count}")
