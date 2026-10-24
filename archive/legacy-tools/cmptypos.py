import sys, os
sys.path.insert(0, r"F:\sr2-cn\pylibs"); sys.path.insert(0, r"F:\sr2-cn")
from sr2lib import Vpp, parse_charlist
from sr2patch import CharList, file_offsets, read_units
G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
W = r"F:\sr2-cn"
def load(p):
    v = Vpp(p)
    raw = bytes(v.read(v.find("charlist_CH","txt")))
    # 两种格式
    cps = [int(l) for l in raw.decode("utf-8").split("\n") if l.strip().isdigit()]
    return v, cps
v3, cps3 = load(G + r"\patch.vpp_pc")
v0, cps0 = load(os.path.join(W,"pristine","patch.vpp_pc"))
print("第三方 %d 项, 原厂 %d 项" % (len(cps3), len(cps0)))
print()
# 定义 slot -> 字符
def dec(vals, cps):
    return "".join(chr(cps[x-0x20]) if 0x20 <= x-0x20 < len(cps) else "·" for x in vals)
# 在第三方里找 HUD 那些短字符串
d3 = bytes(v3.read(v3.find("static_CH","le_strings")))
b,c,oa,offs3 = file_offsets(d3)
recs3 = {}
for off in dict.fromkeys(offs3):
    if not (0 < off <= len(d3)-10): continue
    u,_ = read_units(d3, off+8)
    if u is None: continue
    recs3[off] = [x for x,_ in u]
# 原厂同样
d0 = bytes(v0.read(v0.find("static_CH","le_strings")))
b,c,oa,offs0 = file_offsets(d0)
recs0 = {}
for off in dict.fromkeys(offs0):
    if not (0 < off <= len(d0)-10): continue
    u,_ = read_units(d0, off+8)
    if u is None: continue
    recs0[off] = [x for x,_ in u]
print("第三方记录 %d 条, 原厂 %d 条" % (len(recs3), len(recs0)))
print()
# 找「辩护」
hits = 0
for off, vals in recs3.items():
    t = dec(vals, cps3)
    if "辩护" in t:
        hits += 1
        # 用原厂同 off 解
        t0 = dec(recs0[off], cps0) if off in recs0 else "(原厂无此偏移)"
        print("=== @%d ===" % off)
        print("  第三方: %s" % t[:60])
        print("  原厂  : %s" % t0[:60])
        print("  第三方槽位: %s" % vals[:14])
        if off in recs0: print("  原厂槽位  : %s" % recs0[off][:14])
        print()
        if hits >= 5: break
if hits == 0:
    print("第三方 static_CH 里没有「辩护」")
