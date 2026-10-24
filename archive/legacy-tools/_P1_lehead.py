# -*- coding: utf-8 -*-
"""重新审视：le_strings 头部到底有什么？是否内嵌 charlist？
检查 static_CH / voice_script_CH 的前 200 字节。
"""
import sys, struct
sys.path.insert(0, 'F:/sr2-cn')
from sr2lib import Vpp

G = r'G:\SteamLibrary\steamapps\common\Saints Row 2'
v = Vpp(G + '/patch.vpp_pc')

for nm, ext in [('static_CH', 'le_strings'), ('voice_script_CH', 'le_strings'), ('platform_pc_CH', 'le_strings')]:
    raw = v.read(v.find(nm, ext))
    magic, ver, buckets, count = struct.unpack_from('<IHHI', raw, 0)
    print("=== %s (%d bytes) ===" % (nm, len(raw)))
    print("  magic=0x%08X ver=%d buckets=%d count=%d" % (magic, ver, buckets, count))
    print("  前 64:", raw[:64].hex(' ').upper())
    print("  桶表后(0x%X) 前 48:" % (16 + buckets * 8),
          raw[16 + buckets * 8:16 + buckets * 8 + 48].hex(' ').upper())
    # 桶表内容（前 8 项）
    print("  桶表前 8 项:")
    for i in range(min(8, buckets)):
        o, f = struct.unpack_from('<II', raw, 16 + i * 8)
        print("     [%d] off=0x%X flag=%d" % (i, o, f))
    print()
