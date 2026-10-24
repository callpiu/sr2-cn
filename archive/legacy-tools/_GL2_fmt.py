# -*- coding: utf-8 -*-
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"
v = Vpp(os.path.join(G, "patch.vpp_pc"))
raw = None
for e in v.entries():
    if (e["name"] or "") == "static_CH":
        raw = v.read(e)
print("static_CH %d B" % len(raw))
print("\n--- 头部 0..128 ---")
for off in range(0, 128, 16):
    print("%6d  %s" % (off, " ".join("%02X" % c for c in raw[off:off+16])))
for t, pos in ((0xF284ED87, 209904), (0xAF10621E, 268028)):
    print("\n--- id 0x%08X @%d 附近 ---" % (t, pos))
    a = max(0, pos-32)
    for off in range(a, pos+48, 16):
        mark = " <==" if off <= pos < off+16 else ""
        print("%6d  %s%s" % (off, " ".join("%02X" % c for c in raw[off:off+16]), mark))
    # 尝试把附近当 u32 读
    print("  u32:", [hex(struct.unpack_from("<I", raw, pos-8+i*4)[0]) for i in range(8)])
