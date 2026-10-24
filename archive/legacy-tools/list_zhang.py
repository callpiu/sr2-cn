import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"; W = r"F:\sr2-cn"
v3 = Vpp(os.path.join(G,"patch.vpp_pc"))
v0 = Vpp(os.path.join(W,"pristine","patch.vpp_pc"))
def mkcps(v):
    cps = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    return cps, {i+0x20: chr(cp) for i,cp in enumerate(cps)}
_, S3 = mkcps(v3); _, S0 = mkcps(v0)
def dec(S, vals): return "".join(S.get(x,"·") for x in vals)
print("=== 第三方文本里所有含「丈」的记录 ===")
for nm in ("static_CH","voice_script_CH","platform_pc_CH"):
    e3 = v3.find(nm,"le_strings")
    if not e3: continue
    d3 = bytes(v3.read(e3))
    b,c,oa,offs = file_offsets(d3)
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d3)-10): continue
        u,_ = read_units(d3, off+8)
        if u is None: continue
        vals = [x for x,_ in u]
        t = dec(S3, vals)
        if "丈" in t:
            # 原厂同偏移
            t0 = ""
            e0 = v0.find(nm,"le_strings")
            if e0:
                d0 = bytes(v0.read(e0))
                u0,_ = read_units(d0, off+8)
                t0 = dec(S0, [x for x,_ in u0]) if u0 else ""
            print("  %-16s @%-8d 第三方: %s" % (nm, off, t[:56]))
            print("  %-16s %-9s 原厂  : %s" % ("", "", t0[:56]))
            print("  %-16s %-9s 槽位  : %s" % ("", "", vals[:14]))
            print()
