import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import CharList, file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"; W = r"F:\sr2-cn"
v3 = Vpp(os.path.join(G,"patch.vpp_pc"))
CPS3 = [int(l) for l in v3.read(v3.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S3 = {}   # slot -> 字符
for i,cp in enumerate(CPS3): S3[i+0x20] = chr(cp)
def dec3(vals): return "".join(S3.get(x,"·") for x in vals)

# 原厂：繁中
v0 = Vpp(os.path.join(W,"pristine","patch.vpp_pc"))
CPS0 = [int(l) for l in v0.read(v0.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
S0 = {i+0x20: chr(cp) for i,cp in enumerate(CPS0)}
def dec0(vals): return "".join(S0.get(x,"·") for x in vals)

for nm in ("static_CH","voice_script_CH","platform_pc_CH"):
    e3 = v3.find(nm,"le_strings"); e0 = v0.find(nm,"le_strings")
    if not e3: continue
    d3 = bytes(v3.read(e3)); d0 = bytes(v0.read(e0)) if e0 else None
    b,c,oa,offs = file_offsets(d3)
    hits = 0
    print("=== %s ===" % nm)
    for off in dict.fromkeys(offs):
        if not (0 < off <= len(d3)-10): continue
        u,_ = read_units(d3, off+8)
        if u is None: continue
        vals3 = [x for x,_ in u]
        t3 = dec3(vals3)
        # 找「三」或「王」的短字符串
        if len(t3) <= 14 and ("王" in t3):
            t0 = ""
            if d0:
                u0,_ = read_units(d0, off+8)
                if u0: t0 = dec0([x for x,_ in u0])
            print("  @%-8d 第三方: %-16s 原厂: %-16s 槽位: %s" % (off, t3, t0, vals3[:10]))
            hits += 1
            if hits >= 8: break
    print()
