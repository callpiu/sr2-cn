import os, sys, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
H1, H2 = 0x84F287ED, 0x10AF1E62
v = Vpp(os.path.join(G,"patch.vpp_pc"))
# 列出所有 le_strings 条目
print("=== patch.vpp_pc 的 le_strings 条目 ===")
for e in v.entries():
    if e["ext"]=="le_strings":
        print("  %-24s %d" % (e["name"], e["size"]))
print()
# 在所有条目里找这两个 hash
print("=== 在各条目里查这两个 hash ===")
for e in v.entries():
    if e["ext"] not in ("le_strings",""): continue
    d = bytes(v.read(e))
    # 记录头 4 字节就是 hash（小端）
    for off in range(0, len(d)-4):
        if struct.unpack_from("<I", d, off)[0] in (H1,H2):
            h = struct.unpack_from("<I", d, off)[0]
            print("  %-24s @%-9d hash 0x%08X" % (e["name"], off, h))
