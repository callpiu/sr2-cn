# -*- coding: utf-8 -*-
"""诊断 v415c：枚举记录区起点，找出能数出 12250 条、且正好落在 0x17F2E 的那个。"""
import sys, os, struct
sys.path.insert(0, r"F:/sr2-cn")
sys.path.insert(0, r"F:/sr2-cn/stub")
import sr2lib
sys.stdout.reconfigure(encoding="utf-8")

G = r"G:\SteamLibrary\steamapps\common\Saints Row 2"
vp = sr2lib.Vpp(os.path.join(G, "patch.vpp_pc"))
cps = [int(l) for l in vp.read(vp.find("charlist_CH")).decode("utf-8").split("\n")
       if l.strip().isdigit()]
N = len(cps)
blob = vp.read(vp.find("static_CH"))
L = len(blob)
print("len =", L)

def walk(b, start, limit=None):
    """返回 (记录起点列表, 是否走到底)"""
    o, out = start, []
    e = limit or len(b)
    while o + 2 <= e:
        st = o
        sl = []
        while True:
            if o + 2 > e:
                return out, False
            s = struct.unpack_from(">H", b, o)[0]
            o += 2
            if s == 0:
                break
            sl.append(s)
            if len(sl) > 4000:
                return out, False
        if sl:
            out.append((st, sl))
    return out, True

def valid(sl):
    for s in sl[2:]:
        if s == 0x0A or s == 0x20 or s == 0x09:
            continue
        if not (0x20 <= s < 0x20 + N):
            return False
    return len(sl) >= 2

print("\n候选起点扫描（目标记录起点 0x17F2E = %d）:" % 0x17F2E)
best = None
for cand in range(0xCBE0, 0xCC10):
    recs, done = walk(blob, cand)
    n = len(recs)
    badv = sum(1 for _, sl in recs if not valid(sl))
    starts = set(st for st, _ in recs)
    hit = 0x17F2E in starts
    print("  0x%05X  条数=%-6d 非法=%-5d 走到底=%-5s 命中目标=%s"
          % (cand, n, badv, done, hit))
    if hit and badv == 0 and n >= 12000:
        best = cand
if best:
    print("\n★ 最佳起点 = 0x%X" % best)
else:
    print("\n未在 0xCBE0..0xCC10 找到；扩大范围再试")
    for cand in range(0x8000, 0xCC00, 4):
        recs, done = walk(blob, cand)
        n = len(recs)
        badv = sum(1 for _, sl in recs if not valid(sl))
        starts = set(st for st, _ in recs)
        if 0x17F2E in starts and badv == 0:
            print("  0x%05X 条数=%d 非法=%d 命中 ✓" % (cand, n, badv))
