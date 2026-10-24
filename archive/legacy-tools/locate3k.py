import sys, os, struct
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp
from sr2patch import file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"; W = r"F:\sr2-cn"
v3 = Vpp(os.path.join(G,"patch.vpp_pc"))
v0 = Vpp(os.path.join(W,"pristine","patch.vpp_pc"))
def mkcps(v):
    cps = [int(l) for l in v.read(v.find("charlist_CH","txt")).decode("utf-8").split("\n") if l.strip().isdigit()]
    return {i+0x20: chr(cp) for i,cp in enumerate(cps)}
S3, S0 = mkcps(v3), mkcps(v0)
def dec(S, vals): return "".join(S.get(x,"·") for x in vals)
TARGET = 0x69AD7
d3 = bytes(v3.read(v3.find("static_CH","le_strings")))
d0 = bytes(v0.read(v0.find("static_CH","le_strings")))
b,c,oa,offs = file_offsets(d3)
# 找包含该偏移的记录
cands = [o for o in dict.fromkeys(offs) if o <= TARGET < o+200]
print("命中偏移 %d (0x%X)" % (TARGET, TARGET))
print("包含它的记录起点: %s" % cands)
for off in cands:
    u,_ = read_units(d3, off+8)
    if u is None: continue
    vals = [x for x,_ in u]
    t3 = dec(S3, vals)
    u0,_ = read_units(d0, off+8)
    t0 = dec(S0, [x for x,_ in u0]) if u0 else ""
    print()
    print("  记录 @%d" % off)
    print("    第三方: %r" % t3)
    print("    原厂  : %r" % t0)
    print("    第三方槽位: %s" % vals[:24])
    if u0: print("    原厂槽位  : %s" % [x for x,_ in u0][:24])
    # 定位「丈」在记录内的位置
    for k,x in enumerate(vals):
        if x == 270:
            print("    「丈」= 第 %d 个槽位（值 270）" % k)
        if x == 271:
            print("    「三」= 第 %d 个槽位（值 271）" % k)
