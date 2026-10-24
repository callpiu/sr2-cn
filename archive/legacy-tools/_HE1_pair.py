# -*- coding: utf-8 -*-
import os, sys, re, struct
sys.path.insert(0, r"F:/sr2-cn")
from sr2lib import Vpp
G  = r"G:/SteamLibrary/steamapps/common/Saints Row 2"

def load_cl(buf):
    nums = [int(x) for x in re.findall(rb'\d+', buf)]
    if nums and nums[0] == len(nums) - 1: nums = nums[1:]
    return nums

def parse(data):
    ver, buckets, count = struct.unpack_from("<HHI", data, 4)
    off = 12 + buckets * 8
    ptrs = [struct.unpack_from("<I", data, off + i*4)[0] for i in range(count)]
    out = []; n = len(data)
    for p in ptrs:
        if p == 0 or p >= n - 4: continue
        id1, id2 = struct.unpack_from("<HH", data, p)
        q = p + 4; slots = []
        while q + 2 <= n:
            w = struct.unpack_from(">H", data, q)[0]
            if w == 0: break
            slots.append(w); q += 2
        out.append(((id1 << 16) | id2, slots))
    return out

cn = Vpp(os.path.join(G, "patch.vpp_pc"))
body = load_cl(cn.read(cn.find("charlist_CH", "txt")))
def dec(slots):
    o = []
    for w in slots:
        if w < 0x20: o.append('·'); continue
        i = w - 0x20
        if i >= len(body): return None
        o.append(chr(body[i]))
    return ''.join(o)

recs = []
for e in cn.entries():
    if e['ext'].lower() != 'le_strings': continue
    nm = e['name'] + '.' + e['ext']
    for h, s in parse(cn.read(e)):
        recs.append((nm, h, s))
print("total recs =", len(recs))

# 按前5槽分组
from collections import defaultdict
by5 = defaultdict(list)
for nm, h, s in recs:
    if len(s) >= 7:
        by5[tuple(s[:5])].append((nm, h, s))

found = 0
for key, lst in by5.items():
    if len(lst) < 2: continue
    short = [x for x in lst if 9 <= len(x[2]) <= 13]
    long_ = [x for x in lst if 20 <= len(x[2]) <= 27]
    for a in short:
        for b in long_:
            if a[2][6] == b[2][6]:
                ta, tb = dec(a[2]), dec(b[2])
                if ta and tb:
                    print(f"\n对: {a[0]} {a[1]:08X} ({len(a[2])}槽) / {b[0]} {b[1]:08X} ({len(b[2])}槽)")
                    print(f"   T1 = {ta}")
                    print(f"   T2 = {tb}")
                    found += 1
                    if found > 25: sys.exit(0)
print("found =", found)
