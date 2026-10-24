# -*- coding: utf-8 -*-
import sys, os, struct, hashlib
sys.path.insert(0, r"F:/sr2-cn")
sys.stdout.reconfigure(encoding="utf-8")
from sr2lib import Vpp
G = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def vf3_uv(raw, N):
    # header 0xD0 起 FontCharacter[N]*16，然后 U[N] int32，V[N] int32
    off = 0xD0 + N * 16
    if off + N*4*2 > len(raw):
        return None
    U = list(struct.unpack_from("<%di" % N, raw, off))
    V = list(struct.unpack_from("<%di" % N, raw, off + N*4))
    return U, V

# pegs jap 描述符
v = Vpp(os.path.join(G, "pegs.vpp_pc"))
for e in v.entries():
    if (e["name"] or "") == "jap" and e["ext"] == "":
        raw = v.read(e)
        print("pegs jap 描述符 %d B" % len(raw))
        print("  hex:", " ".join("%02X" % c for c in raw))
        print("  @8=%d @0x0C=%d @0x10=0x%X @0x14=0x%X @0x1C=%dx%d @0x20=0x%X @0x34=%d" % (
            struct.unpack_from("<I", raw, 8)[0], struct.unpack_from("<I", raw, 0x0C)[0],
            struct.unpack_from("<I", raw, 0x10)[0], struct.unpack_from("<I", raw, 0x14)[0],
            struct.unpack_from("<H", raw, 0x1C)[0], struct.unpack_from("<H", raw, 0x1E)[0],
            struct.unpack_from("<I", raw, 0x20)[0], struct.unpack_from("<I", raw, 0x34)[0]))

# jap.vf3_pc 结构
for label, vp in (("common", "common.vpp_pc"), ("patch", "patch.vpp_pc")):
    vv = Vpp(os.path.join(G, vp))
    for e in vv.entries():
        if (e["name"] or "") == "jap" and e["ext"] == "vf3_pc":
            raw = vv.read(e)
            N = struct.unpack_from("<I", raw, 8)[0]
            r = vf3_uv(raw, N)
            print("\n[%s] jap.vf3_pc %d B N=%d" % (label, len(raw), N))
            if r:
                U, V = r
                print("   U 唯一值 %d 个: %s" % (len(set(U)), sorted(set(U))[:8]))
                print("   V 唯一值 %d 个: %s" % (len(set(V)), sorted(set(V))[:8]))
                print("   U[0:6]=%s  V[0:6]=%s" % (U[:6], V[:6]))
            else:
                print("   结构不符，head:", " ".join("%02X" % c for c in raw[:32]))

# 图集对比
for label, vp, nm, ex in (("textures/jap", "textures.vpp_pc", "jap", ""),
                          ("patch/jap.g_peg_pc", "patch.vpp_pc", "jap", "g_peg_pc")):
    vv = Vpp(os.path.join(G, vp))
    for e in vv.entries():
        if (e["name"] or "") == nm and (e["ext"] or "") == ex:
            raw = vv.read(e)
            print("\n[%s] %d B md5=%s head=%s" % (label, len(raw), hashlib.md5(raw).hexdigest()[:12],
                  " ".join("%02X" % c for c in raw[:24])))
