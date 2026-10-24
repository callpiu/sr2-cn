# -*- coding: utf-8 -*-
"""检查 voice_script_CH 是否含我们那两句字幕。"""
import struct
import sys

sys.path.insert(0, r"F:\sr2-cn")
from vpplight import LightVpp
sys.path.insert(0, r"F:\sr2-cn\pylibs")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
TARGET = "兄弟們"

v = Vpp(f"{G}\\patch.vpp_pc")
cn = [int(l) for l in v.read(v.find("charlist_CH", "txt")).decode("utf-8").split("\n")
      if l.strip().isdigit()]
S = {i + 0x20: chr(cp) for i, cp in enumerate(cn)}
print("charlist_CH: %d 项" % len(cn))
print()

for name in ("static_CH", "voice_script_CH", "platform_pc_CH"):
    try:
        d = bytes(v.read(v.find(name, "le_strings")))
    except Exception as ex:
        print("%s: 读取失败 %s" % (name, ex))
        continue
    b, c, oa, offs = file_offsets(d)
    print("=" * 74)
    print("%s  (%d 字节, buckets=%d count=%d)" % (name, len(d), b, c))
    print("=" * 74)
    hits = 0
    for off in [o for o in dict.fromkeys(offs) if 0 < o <= len(d) - 10]:
        try:
            u, _ = read_units(d, off + 8)
        except Exception:
            continue
        if not u:
            continue
        vals = [x for x, _ in u]
        t = "".join(S.get(x, "·") for x in vals)
        if TARGET in t:
            id1, id2 = struct.unpack_from("<HH", d, off)
            print("  hash 0x%08X @%-8d len=%-4d %s" % ((id1 << 16) | id2, off, len(vals), t))
            hits += 1
            if hits >= 12:
                print("  ... (更多省略)")
                break
    if hits == 0:
        print("  ✗ 没有含「%s」的记录" % TARGET)
    print()
