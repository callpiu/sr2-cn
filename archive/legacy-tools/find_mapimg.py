import os, sys
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
print("=== 1. 松散文件里搜 map_mp_bor ===")
for root, dirs, fs in os.walk(G):
    if any(x in root for x in ("_DLSS5_Backup","reshade-shaders","_archive")): continue
    for f in fs:
        if "map_mp_bor" in f.lower() or "chopshop" in f.lower():
            print("  %s" % os.path.relpath(os.path.join(root,f), G))
print()
print("=== 2. VPP 里搜 map_mp_bor_chopshop ===")
for vf in ("patch.vpp_pc","common.vpp_pc","pegs.vpp_pc"):
    p = os.path.join(G,vf)
    if not os.path.exists(p): continue
    try: v = Vpp(p)
    except Exception: continue
    for e in v.entries():
        if "map_mp_bor" in e["name"].lower() or "chopshop" in e["name"].lower():
            print("  %-16s %-34s %-10s %d" % (vf, e["name"], e["ext"] or "-", e["size"]))
print()
print("=== 3. pegs.vpp_pc 里所有 map_mp_bor* 的 PEG 描述符 ===")
p = os.path.join(G,"pegs.vpp_pc")
if os.path.exists(p):
    import struct
    v = Vpp(p)
    n = 0
    for e in v.entries():
        if "map_mp_bor" in e["name"].lower():
            d = bytes(v.read(e))
            if len(d) >= 0x38:
                W,H,F,S = struct.unpack_from("<HHHI", d, 0x1C)
                print("  %-34s %-8s W=%-5d H=%-5d Fmt=%-5d Size=%d" % (e["name"], e["ext"], W,H,F,S))
            else:
                print("  %-34s %-8s %d 字节" % (e["name"], e["ext"], len(d)))
            n += 1
            if n > 10: break
