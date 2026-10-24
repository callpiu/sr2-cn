import os, sys, hashlib, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
H1, H2 = 0x84F287ED, 0x10AF1E62
print("=== 关键文件 md5 ===")
for fn in ("patch.vpp_pc","patch.vpp_pc.before_probe_rec2.bak",
           "patch.vpp_pc.before_probe_both.bak","patch.vpp_pc.before_marks.bak",
           "patch.vpp_pc.v20261012_144927_before_v534.bak",
           "patch.vpp_pc.v20261012_143820_before_ammo.bak"):
    p = os.path.join(G, fn)
    if not os.path.exists(p): continue
    h = hashlib.md5(open(p,'rb').read()).hexdigest()[:8]
    print("  %-50s %s  %d 字节" % (fn, h, os.path.getsize(p)))
print()
print("=== 各文件里的 REC1 / REC2（含标签）===")
for fn in ("patch.vpp_pc","patch.vpp_pc.before_probe_rec2.bak",
           "patch.vpp_pc.v20261012_144927_before_v534.bak"):
    p = os.path.join(G, fn)
    if not os.path.exists(p): continue
    v = Vpp(p)
    cn = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    S = {i+0x20: chr(cp) for i,cp in enumerate(cn)}
    d = bytes(v.read(v.find("static_CH","le_strings")))
    b,c,oa,offs = file_offsets(d)
    print("  %s:" % fn)
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d)-10): continue
        cd = []
        for base in (0,4):
            for endian in ("<",">"):
                if off+base+4 > len(d): continue
                v0, = struct.unpack_from(endian+"H", d, off+base)
                v1, = struct.unpack_from(endian+"H", d, off+base+2)
                cd += [(v0<<16)|v1, (v1<<16)|v0]
        h = H1 if H1 in cd else (H2 if H2 in cd else None)
        if h is None: continue
        u,_ = read_units(d, off+8)
        vals = [x for x,_ in u]
        t = "".join(S.get(x,"·") for x in vals)
        print("     0x%08X len=%-4d %s" % (h, len(vals), t))
    print()
